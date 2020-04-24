import math
import gc
from tqdm import tqdm
from enum import Enum
from exportData.displayShapes import plotGraphObjectGroups, plotDistrict
from exportData.exportData import save_data_to_file_with_description, load_data_from_file_with_description
from formatData.atomicBlock import assignNeighborBlocksFromCandidateBlocks
from formatData.blockBorderGraph import BlockBorderGraph
from formatData.redistrictingGroup import validateContiguousRedistrictingGroups, RedistrictingGroup, \
    assignNeighboringRedistrictingGroupsToRedistrictingGroups, validateRedistrictingGroups, SplitType
from geographyHelper import alignmentOfPolygon, Alignment, mostCardinalOfGeometries, CardinalDirection, \
    weightedForestFireFillGraphObject, polsbyPopperScoreOfPolygon, polygonFromMultipleGeometries, \
    intersectingGeometries, polygonFromMultiplePolygons, findContiguousGroupsOfGraphObjects, boundsIndexFromDirection, \
    isPolygonAGoodDistrictShape, getOppositeDirection, getCWDirection


class District(BlockBorderGraph):
    def __init__(self, childrenGroups):
        BlockBorderGraph.__init__(self)
        self.children = childrenGroups
        self.removeOutdatedNeighborConnections()

    def updateBlockContainerData(self):
        super(District, self).updateBlockContainerData()
        validateContiguousRedistrictingGroups(self.children)

    def getCutStartingCandidates(self):
        longestDirection = alignmentOfPolygon(self.geometry)

        northernStartingCandidate = mostCardinalOfGeometries(geometryList=self.borderChildren,
                                                             direction=CardinalDirection.north)
        westernStartingCandidate = mostCardinalOfGeometries(geometryList=self.borderChildren,
                                                            direction=CardinalDirection.west)
        easternStartingCandidate = mostCardinalOfGeometries(geometryList=self.borderChildren,
                                                            direction=CardinalDirection.east)
        southernStartingCandidate = mostCardinalOfGeometries(geometryList=self.borderChildren,
                                                             direction=CardinalDirection.south)
        if longestDirection == Alignment.northSouth:
            startingGroupCandidates = ((northernStartingCandidate, CardinalDirection.north),
                                       (southernStartingCandidate, CardinalDirection.south),
                                       (westernStartingCandidate, CardinalDirection.west),
                                       (easternStartingCandidate, CardinalDirection.east))
        else:
            startingGroupCandidates = ((westernStartingCandidate, CardinalDirection.west),
                                       (easternStartingCandidate, CardinalDirection.east),
                                       (northernStartingCandidate, CardinalDirection.north),
                                       (southernStartingCandidate, CardinalDirection.south))

        return startingGroupCandidates

    def split_district(self,
                       number_of_districts,
                       population_deviation,
                       weighting_method,
                       breaking_method,
                       total_split_count=None,
                       should_merge_into_former_redistricting_groups=False,
                       should_refill_each_pass=False,
                       should_draw_fill_attempts=False,
                       should_draw_each_step=False,
                       fast_calculations=True,
                       show_detailed_progress=False,
                       should_save_progress=True):
        if total_split_count is None:
            tqdm.write('*** Splitting into {0} districts ***'.format(number_of_districts))
            total_split_count = 0

        districts = []

        if number_of_districts == 1:
            return [self]

        aRatio = math.floor(number_of_districts / 2)
        bRatio = math.ceil(number_of_districts / 2)
        ratio = (aRatio, bRatio)

        districtSplitScores = []
        thisSplitCount = 0
        originalBreakingMethod = breaking_method
        fillOriginDirection = None
        doneFindingSplits = False
        while not doneFindingSplits:
            tqdm.write('   *** Split starting. Using {0} and {1} ***'.format(weighting_method, breaking_method))

            cutDistrictInfo = self.cutDistrictIntoExactRatio(ratio=ratio,
                                                             populationDeviation=population_deviation,
                                                             weightingMethod=weighting_method,
                                                             breakingMethod=breaking_method,
                                                             fillOriginDirection=fillOriginDirection,
                                                             shouldDrawFillAttempts=should_draw_fill_attempts,
                                                             shouldDrawEachStep=should_draw_each_step,
                                                             shouldMergeIntoFormerRedistrictingGroups=should_merge_into_former_redistricting_groups,
                                                             shouldRefillEachPass=should_refill_each_pass,
                                                             fastCalculations=fast_calculations,
                                                             showDetailedProgress=show_detailed_progress,
                                                             shouldSaveProgress=should_save_progress)
            cutDistrict = cutDistrictInfo[0]
            fillOriginDirection = cutDistrictInfo[1]
            thisSplitCount += 1
            if cutDistrict is None:
                tqdm.write('   *** Failed to cut district. Attempt #:{0} for {1} ***'.format(thisSplitCount, id(self)))
                districtSplitScores.append((None, 0, fillOriginDirection, 0))
            else:
                tqdm.write(
                    '   *** Cut district into exact ratio. Attempt #:{0} for {1} ***'.format(thisSplitCount, id(self)))

                aDistrictCandidate = District(childrenGroups=cutDistrict[0])
                bDistrictCandidate = District(childrenGroups=cutDistrict[1])
                isAGood = isPolygonAGoodDistrictShape(districtPolygon=aDistrictCandidate.geometry,
                                                      parentPolygon=self.geometry)
                isBGood = isPolygonAGoodDistrictShape(districtPolygon=bDistrictCandidate.geometry,
                                                      parentPolygon=self.geometry)
                aPolsbyPopperScore = polsbyPopperScoreOfPolygon(aDistrictCandidate.geometry)
                bPolsbyPopperScore = polsbyPopperScoreOfPolygon(bDistrictCandidate.geometry)
                minimumPolsbyPopperScore = min(aPolsbyPopperScore, bPolsbyPopperScore)
                splitScore = 0
                if isAGood:
                    splitScore += 1
                if isBGood:
                    splitScore += 1

                saveDescription = 'SplitCandidate-{0}-{1}-{2}-'.format(id(self), fillOriginDirection, breaking_method)
                save_data_to_file_with_description(data=[aDistrictCandidate, bDistrictCandidate],
                                                   census_year='',
                                                   state_name='',
                                                   description_of_info=saveDescription)
                saveGeometry = (saveDescription,
                                aDistrictCandidate.geometry,
                                bDistrictCandidate.geometry,
                                self.geometry)
                aDistrictCandidate = None
                bDistrictCandidate = None
                gc.collect()

                districtSplitScores.append({'saveDescription': saveDescription,
                                            'splitScore': splitScore,
                                            'fillOriginDirection': fillOriginDirection,
                                            'minimumPolsbyPopperScore': minimumPolsbyPopperScore,
                                            'breaking_method': breaking_method,
                                            'geometryInfo': saveGeometry})

                if splitScore is 2:
                    doneFindingSplits = True
                else:
                    tqdm.write('   *** One or more split candidates is not a good shape! Trying again. ***')
                    if should_merge_into_former_redistricting_groups:
                        tqdm.write('      *** Merging district into starting groups ***')
                        redistrictingGroupsInDistrict = cutDistrict[0] + cutDistrict[1]
                        mergedRedistrictingGroups = mergeCandidatesIntoPreviousGroups(
                            candidates=[redistrictingGroupsInDistrict])[0]
                        tqdm.write('      *** Re-attaching new Redistricting Groups to existing Groups ***')
                        assignNeighboringRedistrictingGroupsToRedistrictingGroups(
                            changedRedistrictingGroups=mergedRedistrictingGroups,
                            allNeighborCandidates=mergedRedistrictingGroups)
                        validateRedistrictingGroups(mergedRedistrictingGroups)
                        self.children = mergedRedistrictingGroups

            splitScoresWithCurrentBreakingMethod = [districtSplitScore for districtSplitScore in districtSplitScores
                                                    if districtSplitScore['breaking_method'] is breaking_method]
            fillOriginDirection = getOppositeDirection(fillOriginDirection)
            directionsTried = [districtSplitScore['fillOriginDirection']
                               for districtSplitScore in splitScoresWithCurrentBreakingMethod]
            if fillOriginDirection in directionsTried:
                fillOriginDirection = getCWDirection(fillOriginDirection)
                if fillOriginDirection in directionsTried:
                    fillOriginDirection = getOppositeDirection(fillOriginDirection)
                    if fillOriginDirection in directionsTried:
                        if breaking_method is BreakingMethod.splitLowestRelativeEnergySeam or breaking_method is BreakingMethod.splitLowestEnergySeam:
                            breaking_method = BreakingMethod.splitGroupsOnEdge
                        else:
                            doneFindingSplits = True

        districtSplitScores.sort(key=lambda x: x['minimumPolsbyPopperScore'], reverse=True)
        save_data_to_file_with_description(data=districtSplitScores,
                                           census_year='',
                                           state_name='',
                                           description_of_info='DistrictSplitScores-{0}'.format(id(self)))
        bestDistrictSplitInfo = districtSplitScores[0]
        bestDistrictSaveDescription = bestDistrictSplitInfo['saveDescription']
        if bestDistrictSaveDescription is None:
            plotDistrict(self, showDistrictNeighborConnections=True)
            raise RuntimeError("Could not find a good split for {0} from list: {1}".format(id(self),
                                                                                           districtSplitScores))
        bestDistrictSplit = load_data_from_file_with_description(census_year='',
                                                                 state_name='',
                                                                 description_of_info=bestDistrictSaveDescription)
        aDistrict = bestDistrictSplit[0]
        bDistrict = bestDistrictSplit[1]
        bestSplitScore = bestDistrictSplitInfo['splitScore']
        bestFillDirection = bestDistrictSplitInfo['fillOriginDirection']
        bestPolsbyPopperScore = bestDistrictSplitInfo['minimumPolsbyPopperScore']
        bestBreakingMethod = bestDistrictSplitInfo['breaking_method']
        tqdm.write('   *** Chose a district split! Ratio: {0}***'.format(ratio))
        tqdm.write('   *** Direction: {0} Split score: {1} Polsby-Popper score: {2} Breaking method: {3} ***'
                   .format(bestFillDirection, bestSplitScore, bestPolsbyPopperScore, bestBreakingMethod))
        total_split_count += 1

        aDistrictSplits = aDistrict.split_district(number_of_districts=aRatio,
                                                   population_deviation=population_deviation,
                                                   weighting_method=weighting_method,
                                                   breaking_method=originalBreakingMethod,
                                                   total_split_count=total_split_count,
                                                   should_merge_into_former_redistricting_groups=should_merge_into_former_redistricting_groups,
                                                   should_refill_each_pass=should_refill_each_pass,
                                                   should_draw_fill_attempts=should_draw_fill_attempts,
                                                   should_draw_each_step=should_draw_each_step,
                                                   fast_calculations=fast_calculations,
                                                   show_detailed_progress=show_detailed_progress,
                                                   should_save_progress=should_save_progress)
        districts.extend(aDistrictSplits)

        bDistrictSplits = bDistrict.split_district(number_of_districts=bRatio,
                                                   population_deviation=population_deviation,
                                                   weighting_method=weighting_method,
                                                   breaking_method=originalBreakingMethod,
                                                   total_split_count=total_split_count,
                                                   should_merge_into_former_redistricting_groups=should_merge_into_former_redistricting_groups,
                                                   should_refill_each_pass=should_refill_each_pass,
                                                   should_draw_fill_attempts=should_draw_fill_attempts,
                                                   should_draw_each_step=should_draw_each_step,
                                                   fast_calculations=fast_calculations,
                                                   show_detailed_progress=show_detailed_progress,
                                                   should_save_progress=should_save_progress)
        districts.extend(bDistrictSplits)

        return districts

    def cutDistrictIntoExactRatio(self, ratio, populationDeviation, weightingMethod, breakingMethod,
                                  fillOriginDirection=None, shouldDrawFillAttempts=False, shouldDrawEachStep=False,
                                  shouldMergeIntoFormerRedistrictingGroups=False, shouldRefillEachPass=False,
                                  fastCalculations=True, showDetailedProgress=False, shouldSaveProgress=True):

        ratioTotal = ratio[0] + ratio[1]
        idealDistrictASize = int(self.population / (ratioTotal / ratio[0]))
        idealDistrictBSize = int(self.population / (ratioTotal / ratio[1]))
        candidateDistrictA = []
        candidateDistrictB = []
        districtStillNotExactlyCut = True
        tqdm.write(
            '   *** Attempting forest fire fill for a {0} to {1} ratio on: ***'.format(ratio[0], ratio[1], id(self)))

        districtAStartingGroup = None
        count = 1
        while districtStillNotExactlyCut:
            tqdm.write('      *** Starting forest fire fill pass #{0} ***'.format(count))

            if districtAStartingGroup is None:
                if len(candidateDistrictA) == 0:
                    districtAStartingGroup = None
                else:
                    if shouldRefillEachPass:
                        districtAStartingGroup = None
                    else:
                        districtAStartingGroup = candidateDistrictA

            if breakingMethod is BreakingMethod.splitBestCandidateGroup:
                returnBestCandidateGroup = True
            else:
                returnBestCandidateGroup = False

            districtCandidateResult = self.cutDistrictIntoRoughRatio(idealDistrictASize=idealDistrictASize,
                                                                     weightingMethod=weightingMethod,
                                                                     districtAStartingGroup=districtAStartingGroup,
                                                                     fillOriginDirection=fillOriginDirection,
                                                                     shouldDrawEachStep=shouldDrawEachStep,
                                                                     returnBestCandidateGroup=returnBestCandidateGroup,
                                                                     fastCalculations=fastCalculations)
            districtCandidates = districtCandidateResult[0]
            nextBestGroupForCandidateDistrictA = districtCandidateResult[1]
            fillOriginDirection = districtCandidateResult[2]
            districtAStartingGroup = districtCandidateResult[3]

            candidateDistrictA = districtCandidates[0]
            candidateDistrictB = districtCandidates[1]

            if shouldDrawFillAttempts:
                if nextBestGroupForCandidateDistrictA is None:
                    nextBestGroupForCandidateDistrictA = []
                plotGraphObjectGroups(
                    graphObjectGroups=[candidateDistrictA, candidateDistrictB, nextBestGroupForCandidateDistrictA],
                    showDistrictNeighborConnections=True,
                    saveImages=True,
                    saveDescription='DistrictSplittingIteration-{0}-{1}'.format(id(self), count))

            candidateDistrictAPop = sum(group.population for group in candidateDistrictA)
            candidateDistrictBPop = sum(group.population for group in candidateDistrictB)

            if idealDistrictASize - populationDeviation <= candidateDistrictAPop <= idealDistrictASize + populationDeviation and \
                    idealDistrictBSize - populationDeviation <= candidateDistrictBPop <= idealDistrictBSize + populationDeviation:
                districtStillNotExactlyCut = False
            else:
                tqdm.write('      *** Unsuccessful fill attempt. {0} off the count. ***'
                           .format(abs(idealDistrictASize - candidateDistrictAPop)))
                if len(self.children) == 1:
                    # this means that the candidate couldn't fill because there a single redistricting group
                    # likely because there was a single county
                    groupsToBreakUp = [(self.children[0], Alignment.all)]
                elif len(candidateDistrictA) == 0:
                    # we didn't get anything in candidateA, which means none of the children met the conditions
                    # so, we won't get anything to break up, let's break the first starting candidate with instead
                    breakupCandidates = [startingCandidateTuple[0]
                                         for startingCandidateTuple in self.getCutStartingCandidates()]
                    breakupCandidates = [breakupCandidate for breakupCandidate in breakupCandidates
                                         if len(breakupCandidate.children) > 1]
                    if len(breakupCandidates) == 0:
                        save_data_to_file_with_description(data=[self, districtAStartingGroup, ratio,
                                                                 candidateDistrictA, candidateDistrictB,
                                                                 nextBestGroupForCandidateDistrictA, breakupCandidates],
                                                           census_year='',
                                                           state_name='',
                                                           description_of_info='ErrorCase-NoGroupsCandidatesCapableOfBreaking')

                        tqdm.write(
                            '   *** Failed fill attempt!!! *** <------------------------------------------------------')
                        tqdm.write("Couldn't fill and all breakup candidates have too few children!!!! For {0}".format(
                            id(self)))
                        return None, fillOriginDirection
                    groupsToBreakUp = [(breakupCandidates[0], Alignment.all)]
                else:
                    if len(candidateDistrictB) == 1:
                        groupsToBreakUp = [(candidateDistrictB[0], Alignment.all)]
                    else:
                        if breakingMethod is BreakingMethod.splitBestCandidateGroup:
                            groupsToBreakUp = [(nextBest, Alignment.all) for nextBest in nextBestGroupForCandidateDistrictA]
                        elif breakingMethod is BreakingMethod.splitGroupsOnEdge:
                            groupsToBreakUp = splitGroupsOnEdge(candidateDistrictA,
                                                                candidateDistrictB,
                                                                shouldMergeIntoFormerRedistrictingGroups,
                                                                shouldRefillEachPass)
                        elif breakingMethod is BreakingMethod.splitLowestEnergySeam:
                            groupsToBreakUp = splitLowestEnergySeam(candidateDistrictA,
                                                                    candidateDistrictB,
                                                                    showDetailedProgress,
                                                                    energyRelativeToPopulation=False)
                        elif breakingMethod is BreakingMethod.splitLowestRelativeEnergySeam:
                            groupsToBreakUp = splitLowestEnergySeam(candidateDistrictA,
                                                                    candidateDistrictB,
                                                                    showDetailedProgress,
                                                                    energyRelativeToPopulation=True)
                        else:
                            raise RuntimeError('{0} is not supported'.format(breakingMethod))

                groupsCapableOfBreaking = [groupToBreakUp for groupToBreakUp in groupsToBreakUp
                                           if len(groupToBreakUp[0].children) > 1]
                if len(groupsCapableOfBreaking) == 0:
                    save_data_to_file_with_description(data=[self, districtAStartingGroup, ratio,
                                                             candidateDistrictA, candidateDistrictB,
                                                             nextBestGroupForCandidateDistrictA],
                                                       census_year='',
                                                       state_name='',
                                                       description_of_info='ErrorCase-NoGroupsCapableOfBreaking')
                    plotGraphObjectGroups([self.children, districtAStartingGroup])
                    raise RuntimeError("Groups to break up don't meet criteria. Groups: {0}".format(
                        [groupToBreakUp[0].graphId for groupToBreakUp in groupsToBreakUp]
                    ))

                tqdm.write(
                    '      *** Graph splitting {0} redistricting groups ***'.format(len(groupsCapableOfBreaking)))
                updatedChildren = self.children.copy()
                newRedistrictingGroups = []
                if showDetailedProgress:
                    pbar = None
                else:
                    pbar = tqdm(total=len(groupsCapableOfBreaking))
                for groupToBreakUpItem in groupsCapableOfBreaking:
                    if showDetailedProgress:
                        countForProgress = groupsCapableOfBreaking.index(groupToBreakUpItem) + 1
                    else:
                        countForProgress = None
                    groupToBreakUp = groupToBreakUpItem[0]
                    alignmentForSplits = groupToBreakUpItem[1]
                    smallerRedistrictingGroups = groupToBreakUp.getGraphSplits(shouldDrawGraph=shouldDrawEachStep,
                                                                               alignment=alignmentForSplits,
                                                                               countForProgress=countForProgress)
                    updatedChildren.extend(smallerRedistrictingGroups)
                    updatedChildren.remove(groupToBreakUp)

                    # assign the previous parent graphId so that we can combine the parts again after the exact split
                    for smallerRedistrictingGroup in smallerRedistrictingGroups:
                        if groupToBreakUp.previousParentId is None:
                            previousParentId = groupToBreakUp.graphId
                        else:
                            previousParentId = groupToBreakUp.previousParentId
                        smallerRedistrictingGroup.previousParentId = previousParentId

                    newRedistrictingGroups.extend(smallerRedistrictingGroups)
                    if pbar is not None:
                        pbar.update(1)
                if pbar is not None:
                    pbar.close()

                tqdm.write('      *** Re-attaching new Redistricting Groups to existing Groups ***')
                assignNeighboringRedistrictingGroupsToRedistrictingGroups(
                    changedRedistrictingGroups=newRedistrictingGroups,
                    allNeighborCandidates=updatedChildren)
                validateRedistrictingGroups(updatedChildren)

                tqdm.write('      *** Updating District Candidate Data ***')
                self.children = updatedChildren

                # need to make sure the starting group still is in the district
                if districtAStartingGroup not in self.children:
                    districtAStartingGroup = None

            shouldSaveThisPass = True
            if breakingMethod is BreakingMethod.splitLowestEnergySeam:
                if count % 10 != 0:
                    shouldSaveThisPass = False

            if shouldSaveProgress:
                if shouldSaveThisPass:
                    save_data_to_file_with_description(data=(self, candidateDistrictA, ratio, fillOriginDirection),
                                                       census_year='',
                                                       state_name='',
                                                       description_of_info='DistrictSplitLastIteration-{0}'.format(id(self)))
            count += 1

        if shouldMergeIntoFormerRedistrictingGroups:
            tqdm.write('      *** Merging candidates into remaining starting groups ***')
            mergedCandidates = mergeCandidatesIntoPreviousGroups(
                candidates=[candidateDistrictA, candidateDistrictB])
            candidateDistrictA = mergedCandidates[0]
            candidateDistrictB = mergedCandidates[1]
            tqdm.write('      *** Re-attaching new Redistricting Groups to existing Groups ***')
            assignNeighboringRedistrictingGroupsToRedistrictingGroups(
                changedRedistrictingGroups=candidateDistrictA,
                allNeighborCandidates=candidateDistrictA)
            assignNeighboringRedistrictingGroupsToRedistrictingGroups(
                changedRedistrictingGroups=candidateDistrictB,
                allNeighborCandidates=candidateDistrictB)
            validateRedistrictingGroups(candidateDistrictA)
            validateRedistrictingGroups(candidateDistrictB)

        tqdm.write(
            '   *** Successful fill attempt!!! *** <------------------------------------------------------------')
        return (candidateDistrictA, candidateDistrictB), fillOriginDirection

    def cutDistrictIntoRoughRatio(self, idealDistrictASize, weightingMethod, districtAStartingGroup=None,
                                  fillOriginDirection=None, shouldDrawEachStep=False, returnBestCandidateGroup=False,
                                  fastCalculations=True):
        if districtAStartingGroup:
            startingGroupCandidates = [(districtAStartingGroup.copy(), fillOriginDirection)]
        else:
            startingGroupCandidates = [([startingGroupCandidate], direction)
                                       for startingGroupCandidate, direction in self.getCutStartingCandidates()]
            if fillOriginDirection is not None:
                startingGroupCandidates = [(startingGroupCandidateGroup, direction)
                                           for startingGroupCandidateGroup, direction in startingGroupCandidates
                                           if direction is fillOriginDirection]

        i = 0
        startingObjects = []
        candidateDistrictA = []
        nextBestGroupFromCandidateDistrictA = None
        while not candidateDistrictA and i < len(startingGroupCandidates):
            startingObjects = startingGroupCandidates[i][0]
            fillOriginDirection = startingGroupCandidates[i][1]

            def withinIdealDistrictSize(currentGroups, candidateGroups):
                currentPop = sum(group.population for group in currentGroups)
                candidatePop = sum(group.population for group in candidateGroups)
                proposedPop = currentPop + candidatePop
                isWithinIdealPop = proposedPop <= idealDistrictASize
                proposedPopDiff = idealDistrictASize - proposedPop
                return isWithinIdealPop, proposedPopDiff

            def polsbyPopperScoreOfCombinedGeometry(currentGroupPolygon, remainingGroups, candidateGroups,
                                                    fastCalculations=True):
                candidateGroupsPolygon = polygonFromMultipleGeometries(candidateGroups,
                                                                       useEnvelope=fastCalculations)
                # never useEnvelope here, because currentGroupPolygon is our cached shape
                candidatePolygon = polygonFromMultiplePolygons([currentGroupPolygon, candidateGroupsPolygon])
                combinedRemainingPolygon = polygonFromMultipleGeometries(remainingGroups,
                                                                         useEnvelope=fastCalculations)

                score = polsbyPopperScoreOfPolygon(candidatePolygon)
                remainingScore = polsbyPopperScoreOfPolygon(combinedRemainingPolygon)
                minimumPolsbyPopperScore = min(score, remainingScore)

                return minimumPolsbyPopperScore

            def distanceScoreOfCombinedGeometry(currentGroupPolygon, remainingGroups, candidateGroups,
                                                fastCalculations=True):
                candidateGroupsPolygon = polygonFromMultipleGeometries(candidateGroups,
                                                                       useEnvelope=fastCalculations)
                distance = currentGroupPolygon.centroid.distance(candidateGroupsPolygon.centroid)
                score = 1 / distance

                return score

            def cardinalDirectionScoreOfCandidateGroups(currentGroupPolygon, remainingGroups, candidateGroups,
                                                        fastCalculations=True):
                boundsIndex = boundsIndexFromDirection(fillOriginDirection)
                directionReferenceValue = self.geometry.bounds[boundsIndex]
                candidateGroupsPolygon = polygonFromMultipleGeometries(candidateGroups,
                                                                       useEnvelope=fastCalculations)
                candidateGroupsValue = candidateGroupsPolygon.bounds[boundsIndex]
                difference = directionReferenceValue - candidateGroupsValue
                difference = math.fabs(difference)
                if difference == 0:
                    score = math.inf
                else:
                    score = 1 / difference

                return score

            if weightingMethod is WeightingMethod.distance:
                chosenWeightingAlgorithm = distanceScoreOfCombinedGeometry
            elif weightingMethod is WeightingMethod.polsbyPopper:
                chosenWeightingAlgorithm = polsbyPopperScoreOfCombinedGeometry
            elif weightingMethod is WeightingMethod.cardinalDistance:
                chosenWeightingAlgorithm = cardinalDirectionScoreOfCandidateGroups
            else:
                raise RuntimeError('Must choose a weighting method. {0} is not supported'.format(weightingMethod))

            candidateDistrictAResult = weightedForestFireFillGraphObject(candidateObjects=self.children,
                                                                         startingObjects=startingObjects,
                                                                         condition=withinIdealDistrictSize,
                                                                         weightingScore=chosenWeightingAlgorithm,
                                                                         shouldDrawEachStep=shouldDrawEachStep,
                                                                         returnBestCandidateGroup=returnBestCandidateGroup,
                                                                         fastCalculations=fastCalculations)
            candidateDistrictA = candidateDistrictAResult[0]
            nextBestGroupFromCandidateDistrictA = candidateDistrictAResult[1]
            i += 1

        candidateDistrictB = [group for group in self.children if group not in candidateDistrictA]
        return (candidateDistrictA,
                candidateDistrictB), nextBestGroupFromCandidateDistrictA, fillOriginDirection, startingObjects


def create_district_from_redistricting_groups(redistricting_groups):
    initialDistrict = District(childrenGroups=redistricting_groups)
    return initialDistrict


def getRedistrictingGroupsBetweenCandidates(aCandidate, bCandidate):
    groupsBetween = []

    for aGroup in aCandidate:
        for bGroup in bCandidate:
            if intersectingGeometries(aGroup, bGroup):
                if aGroup not in groupsBetween:
                    groupsBetween.append(aGroup)
                if bGroup not in groupsBetween:
                    groupsBetween.append(bGroup)

    return groupsBetween


def mergeCandidatesIntoPreviousGroups(candidates):
    mergedCandidates = []
    for candidate in candidates:

        # group redistricting groups together based on previous parent
        parentDict = {}
        for redistrictingGroup in candidate:
            # if it doesn't have a previous parent, that means it wasn't broken up, so we will just let is pass through
            if redistrictingGroup.previousParentId is None:
                parentDict[redistrictingGroup.graphId] = [redistrictingGroup]
            else:
                if redistrictingGroup.previousParentId in parentDict:
                    parentDict[redistrictingGroup.previousParentId].append(redistrictingGroup)
                else:
                    parentDict[redistrictingGroup.previousParentId] = [redistrictingGroup]

        # merge the grouped groups together
        mergedRedistrictingGroups = []
        with tqdm(total=len(parentDict)) as pbar:
            for redistrictingGroupList in parentDict.values():
                if len(redistrictingGroupList) == 1:
                    mergedRedistrictingGroups.append(redistrictingGroupList[0])
                else:
                    allBorderBlocks = []
                    allBlocks = []
                    for redistrictingGroup in redistrictingGroupList:
                        allBorderBlocks.extend(redistrictingGroup.borderChildren)
                        allBlocks.extend(redistrictingGroup.children)

                    # assign block neighbors to former border blocks
                    tqdm.write('      *** Starting a merge with {0} border blocks and {1} total blocks ***'.format(
                        len(allBorderBlocks), len(allBlocks)))
                    for formerBorderBlock in allBorderBlocks:
                        assignNeighborBlocksFromCandidateBlocks(block=formerBorderBlock,
                                                                candidateBlocks=allBlocks)

                    contiguousRegions = findContiguousGroupsOfGraphObjects(allBlocks)

                    mergedRedistrictingGroupsForPrevious = []
                    for contiguousRegion in contiguousRegions:
                        contiguousRegionGroup = RedistrictingGroup(childrenBlocks=contiguousRegion)
                        # assign block neighbors to former border blocks
                        for borderBlock in contiguousRegionGroup.borderChildren:
                            assignNeighborBlocksFromCandidateBlocks(block=borderBlock,
                                                                    candidateBlocks=contiguousRegionGroup.children)
                        contiguousRegionGroup.validateBlockNeighbors()
                        mergedRedistrictingGroupsForPrevious.append(contiguousRegionGroup)
                    mergedRedistrictingGroups.extend(mergedRedistrictingGroupsForPrevious)
                pbar.update(1)

        mergedCandidates.append(mergedRedistrictingGroups)

    return mergedCandidates


def splitGroupsOnEdge(candidateDistrictA,
                      candidateDistrictB,
                      shouldMergeIntoFormerRedistrictingGroups,
                      shouldRefillEachPass):
    groupsBetweenCandidates = getRedistrictingGroupsBetweenCandidates(candidateDistrictA,
                                                                      candidateDistrictB)
    # if we are refilling each time and merging after a split,
    # we can break up groups on both sides of the boundary
    if shouldMergeIntoFormerRedistrictingGroups and shouldRefillEachPass:
        groupsToBreakUp = groupsBetweenCandidates
    else:
        groupsToBreakUp = [groupToBreakUp for groupToBreakUp in groupsBetweenCandidates
                           if groupToBreakUp not in candidateDistrictA]
    groupsToBreakUp = [(groupToBreakUp, Alignment.all) for groupToBreakUp in groupsToBreakUp]
    return groupsToBreakUp


def splitLowestEnergySeam(candidateDistrictA, candidateDistrictB,
                          showDetailedProgress, energyRelativeToPopulation):
    groupsBetweenCandidates = getRedistrictingGroupsBetweenCandidates(candidateDistrictA,
                                                                      candidateDistrictB)
    groupBreakUpCandidates = [groupToBreakUp for groupToBreakUp in groupsBetweenCandidates
                              if groupToBreakUp not in candidateDistrictA]
    groupBreakUpCandidates = [groupBreakUpCandidate
                              for groupBreakUpCandidate in groupBreakUpCandidates
                              if len(groupBreakUpCandidate.children) > 1 and groupBreakUpCandidate.population > 0]
    seamsToEvaluate = []
    for groupBreakUpCandidate in groupBreakUpCandidates:
        westernAndEasternNeighbors = groupBreakUpCandidate.westernNeighbors + groupBreakUpCandidate.easternNeighbors
        if any([neighbor for neighbor in westernAndEasternNeighbors
                if neighbor in candidateDistrictA]):
            seamsToEvaluate.append((groupBreakUpCandidate, Alignment.westEast))

        northernAndSouthernNeighbors = groupBreakUpCandidate.northernNeighbors + groupBreakUpCandidate.southernNeighbors
        if any([neighbor for neighbor in northernAndSouthernNeighbors
                if neighbor in candidateDistrictA]):
            seamsToEvaluate.append((groupBreakUpCandidate, Alignment.northSouth))
    tqdm.write(
        '      *** Finding lowest energy seam out of {0} seams ***'.format(len(seamsToEvaluate)))
    if showDetailedProgress:
        pbar = None
    else:
        pbar = tqdm(total=len(seamsToEvaluate))
    energyScores = []
    backupEnergyScores = []
    for seamToEvaluate in seamsToEvaluate:
        groupToEvaluate = seamToEvaluate[0]
        alignmentForEvaluation = seamToEvaluate[1]
        groupToEvaluate.fillPopulationEnergyGraph(alignmentForEvaluation)
        splitResult = groupToEvaluate.getPopulationEnergyPolygonSplit(alignmentForEvaluation)
        groupToEvaluate.clearPopulationEnergyGraph()
        polygonSplitResultType = splitResult[0]

        if polygonSplitResultType is SplitType.NoSplit:
            # if we can't split in this direction, we need to check the other direction
            # and if that direction can't be split, we'll call for a force split
            if alignmentForEvaluation is Alignment.northSouth:
                oppositeAlignment = Alignment.westEast
            else:
                oppositeAlignment = Alignment.northSouth

            groupToEvaluate.fillPopulationEnergyGraph(oppositeAlignment)
            oppositeSplitResult = groupToEvaluate.getPopulationEnergyPolygonSplit(oppositeAlignment)
            groupToEvaluate.clearPopulationEnergyGraph()
            oppositePolygonSplitResultType = oppositeSplitResult[0]
            if oppositePolygonSplitResultType is SplitType.NoSplit:
                seamEnergy = groupToEvaluate.population
                alignmentForEvaluation = Alignment.all
                energyScores.append((groupToEvaluate, alignmentForEvaluation,
                                     seamEnergy, polygonSplitResultType))

                if len(groupToEvaluate.children) >= 10:
                    tqdm.write(
                        "      *** Warning: Couldn't find a split for {0}. Candidate for Force Splitting. {1} blocks. {2} total pop.".format(
                            groupToEvaluate.graphId, len(groupToEvaluate.children),
                            groupToEvaluate.population))
                    save_data_to_file_with_description(data=groupToEvaluate,
                                                       census_year='',
                                                       state_name='',
                                                       description_of_info='WarningCase-ForceSplittingWithOver10Children-{0}'
                                                       .format(id(groupToEvaluate)))
            else:
                if oppositePolygonSplitResultType is SplitType.ForceSplitAllBlocks:
                    # will need to remove any other seams in list if we ever take
                    # more than the first seam in the sorted list below
                    seamEnergy = groupToEvaluate.population
                    alignmentForEvaluation = Alignment.all
                else:
                    seamEnergy = oppositeSplitResult[3]
                    alignmentForEvaluation = oppositeAlignment
                backupEnergyScores.append((groupToEvaluate, alignmentForEvaluation,
                                           seamEnergy, oppositePolygonSplitResultType))
        else:
            if polygonSplitResultType is SplitType.ForceSplitAllBlocks:
                # will need to remove any other seams in list if we ever take
                # more than the first seam in the sorted list below
                seamEnergy = groupToEvaluate.population
                alignmentForEvaluation = Alignment.all
            else:
                seamEnergy = splitResult[3]
            energyScores.append((groupToEvaluate, alignmentForEvaluation,
                                 seamEnergy, polygonSplitResultType))
        if pbar is not None:
            pbar.update(1)
    if pbar is not None:
        pbar.close()
    if len(energyScores) == 0:
        tqdm.write("      *** Warning: Did not find any energy scores in this list: {0}".format(
            [group.graphId for group in groupBreakUpCandidates]))
        tqdm.write("          Switching to backup scores: {0} ***".format(backupEnergyScores))
        energyScores = backupEnergyScores

    if energyRelativeToPopulation:
        relativeEnergyScores = []
        for energyScore in energyScores:
            scoreGroup = energyScore[0]
            scoreAlignment = energyScore[1]
            currentScore = energyScore[2]
            scoreSplitResultType = energyScore[3]
            newScore = currentScore / scoreGroup.population
            relativeEnergyScores.append((scoreGroup, scoreAlignment, newScore, scoreSplitResultType))
        energyScores = relativeEnergyScores

    energyScores.sort(key=lambda x: x[2])
    minimumEnergySeam = energyScores[0]
    groupToBreakUp = minimumEnergySeam[0]
    groupToBreakUpSeamAlignment = minimumEnergySeam[1]
    groupsToBreakUp = [(groupToBreakUp, groupToBreakUpSeamAlignment)]
    return groupsToBreakUp


class WeightingMethod(Enum):
    distance = 0
    polsbyPopper = 1
    cardinalDistance = 2


class BreakingMethod(Enum):
    splitBestCandidateGroup = 0
    splitGroupsOnEdge = 1
    splitLowestEnergySeam = 2
    splitLowestRelativeEnergySeam = 2
