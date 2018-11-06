"""
Last edited: May 13 2018

@author: Lara Welder
"""
import warnings
import pandas as pd
import FINE as fn


def isString(string):
    """ Checks if the input argument is a string """
    if not type(string) == str:
        raise TypeError("The input argument has to be a string")


def equalStrings(ref, test):
    """ Checks if two strings are equal to each other """
    if ref != test:
        print('Reference string: ' + str(ref))
        print('String: ' + str(test))
        raise ValueError('Strings do not match')


def isStrictlyPositiveInt(value):
    """ Checks if the input argument is a strictly positive integer """
    if not type(value) == int:
        raise TypeError("The input argument has to be an integer")
    if not value > 0:
        raise ValueError("The input argument has to be strictly positive")


def isStrictlyPositiveNumber(value):
    """ Checks if the input argument is a strictly positive number """
    if not (type(value) == float or type(value) == int):
        raise TypeError("The input argument has to be an number")
    if not value > 0:
        raise ValueError("The input argument has to be strictly positive")


def isPositiveNumber(value):
    """ Checks if the input argument is a positive number """
    if not (type(value) == float or type(value) == int):
        raise TypeError("The input argument has to be an number")
    if not value >= 0:
        raise ValueError("The input argument has to be positive")


def isSetOfStrings(setOfStrings):
    """ Checks if the input argument is a set of strings """
    if not type(setOfStrings) == set:
        raise TypeError("The input argument has to be a set")
    if not any([type(r) == str for r in setOfStrings]):
        raise TypeError("The list entries in the input argument must be strings")


def isEnergySystemModelInstance(esM):
    if not isinstance(esM, fn.EnergySystemModel):
        raise TypeError('The input is not an EnergySystemModel instance.')


def checkEnergySystemModelInput(locations, commodities, commoditiyUnitsDict, numberOfTimeSteps, hoursPerTimeStep,
                                costUnit, lengthUnit):
    """ Checks input arguments of an EnergySystemModel instance for value/type correctness """

    # Locations and commodities have to be sets
    isSetOfStrings(locations), isSetOfStrings(commodities)

    # The commodityUnitDict has to be a dictionary which keys equal the specified commodities and which values are
    # strings
    if not type(commoditiyUnitsDict) == dict:
        raise TypeError("The commoditiyUnitsDict input argument has to be a dictionary.")
    if commodities != set(commoditiyUnitsDict.keys()):
        raise ValueError("The keys of the commodityUnitDict must equal the specified commodities.")
    isSetOfStrings(set(commoditiyUnitsDict.values()))

    # The numberOfTimeSteps and the hoursPerTimeStep have to be strictly positive numbers
    isStrictlyPositiveInt(numberOfTimeSteps), isStrictlyPositiveNumber(hoursPerTimeStep)

    # The costUnit and lengthUnit input parameter have to be strings
    isString(costUnit), isString(lengthUnit)


def checkTimeUnit(timeUnit):
    """
    Function used when an EnergySystemModel instance is initialized
    Checks if the timeUnit input argument is equal to 'h'
    """
    if not timeUnit == 'h':
        raise ValueError("The timeUnit input argument has to be \'h\'")


def checkTimeSeriesIndex(esM, data):
    if list(data.index) != esM._totalTimeSteps:
        raise ValueError('Time indices do not match the one of the specified energy system model.\n' +
                         'Data indicies: ' + str(set(data.index)) + '\n' +
                         'Energy system model time steps: ' + str(esM._timeSteps))


def checkRegionalColumnTitles(esM, data):
    if set(data.columns) != esM._locations:
        raise ValueError('Location indices do not match the one of the specified energy system model.\n' +
                         'Data columns: ' + str(set(data.columns)) + '\n' +
                         'Energy system model regions: ' + str(esM._locations))


def checkRegionalIndex(esM, data):
    if set(data.index) != esM._locations:
        raise ValueError('Location indices do not match the one of the specified energy system model.\n' +
                         'Data indicies: ' + str(set(data.index)) + '\n' +
                         'Energy system model regions: ' + str(esM._locations))


def checkConnectionIndex(data, locationalEligibility):
    if not set(data.index) == set(locationalEligibility.index):
        raise ValueError('Indices do not match the eligible connections of the component.\n' +
                         'Data indicies: ' + str(set(data.index)) + '\n' +
                         'Eligible connections: ' + str(set(locationalEligibility.index)))


def checkCommodities(esM, commodity):
    if not commodity.issubset(esM._commodities):
        raise ValueError('Location indices do not match the one of the specified energy system model.\n' +
                         'Commodity: ' + str(set(commodity)) + '\n' +
                         'Energy system model regions: ' + str(esM._commodities))


def checkAndSetDistances(distances, locationalEligibility):
    if distances is None:
        print('The distances of a component are set to a normalized values of 1.')
        distances = pd.Series([1 for loc in locationalEligibility.index], index=locationalEligibility.index)
    else:
        if not isinstance(distances, pd.Series):
            raise TypeError('Input data has to be a pandas DataFrame or Series')
        if (distances < 0).any():
            raise ValueError('Distance values smaller than 0 were detected.')
        checkConnectionIndex(distances, locationalEligibility)
    return distances


def checkAndSetTransmissionLosses(losses, distances, locationalEligibility):
    if not (isinstance(losses, int) or isinstance(losses, float) or isinstance(losses, pd.DataFrame)
            or isinstance(losses, pd.Series)):
        raise TypeError('The input data has to be a number, a pandas DataFrame or a pandas Series.')

    if isinstance(losses, int) or isinstance(losses, float):
        if losses < 0 or losses > 1:
            raise ValueError('Losses have to be values between 0 <= losses <= 1.')
        return pd.Series([float(losses) for loc in locationalEligibility.index], index=locationalEligibility.index)
    checkConnectionIndex(losses, locationalEligibility)

    _losses = losses.astype(float)
    if _losses.isnull().any():
        raise ValueError('The losses parameter contains values which are not a number.')
    if (_losses < 0).any() or (_losses > 1).any():
            raise ValueError('Losses have to be values between 0 <= losses <= 1.')
    if (1-losses*distances < 0).any():
        raise ValueError('The losses per distance multiplied with the distances result in negative values.')

    return _losses


def getCapitalChargeFactor(interestRate, economicLifetime):
    """ Computes and returns capital charge factor (inverse of annuity factor) """
    CCF = 1 / interestRate - 1 / (pow(1 + interestRate, economicLifetime) * interestRate)
    CCF = CCF.fillna(economicLifetime)
    return CCF


def checkLocationSpecficDesignInputParams(esM, hasCapacityVariable, hasIsBuiltBinaryVariable,
                                          capacityMin, capacityMax, capacityFix,
                                          locationalEligibility, isBuiltFix, sharedPotentialID, dimension):
    for data in [capacityMin, capacityFix, capacityMax, locationalEligibility, isBuiltFix]:
        if data is not None:
            if dimension == '1dim':
                if not isinstance(data, pd.Series):
                    raise TypeError('Input data has to be a pandas Series')
                checkRegionalIndex(esM, data)
            elif dimension == '2dim':
                if not isinstance(data, pd.Series):
                    raise TypeError('Input data has to be a pandas DataFrame')
                checkConnectionIndex(data, locationalEligibility)
            else:
                raise ValueError("The dimension parameter has to be either \'1dim\' or \'2dim\' ")

    if capacityMin is not None and (capacityMin < 0).any():
        raise ValueError('capacityMin values smaller than 0 were detected.')

    if capacityFix is not None and (capacityFix < 0).any():
        raise ValueError('capacityFix values smaller than 0 were detected.')

    if capacityMax is not None and (capacityMax < 0).any():
        raise ValueError('capacityMax values smaller than 0 were detected.')

    if (capacityMin is not None or capacityMax is not None or capacityFix is not None) and not hasCapacityVariable:
        raise ValueError('Capacity bounds are given but hasDesignDimensionVar was set to False.')

    if isBuiltFix is not None and not hasIsBuiltBinaryVariable:
        raise ValueError('Fixed design decisions are given but hasIsBuiltBinaryVariable was set to False.')

    if sharedPotentialID is not None:
        isString(sharedPotentialID)

    if sharedPotentialID is not None and capacityMax is None:
        raise ValueError('A capacityMax parameter is required if a sharedPotentialID is considered.')

    if capacityMin is not None and capacityMax is not None:
        if (capacityMin > capacityMax).any():
            raise ValueError('capacityMin values > capacityMax values detected.')

    if capacityFix is not None and capacityMax is not None:
        if (capacityFix > capacityMax).any():
            raise ValueError('capacityFix values > capacityMax values detected.')

    if capacityFix is not None and capacityMin is not None:
        if (capacityFix < capacityMin).any():
            raise ValueError('capacityFix values < capacityMax values detected.')

    if locationalEligibility is not None:
        # Check if values are either one or zero
        if ((locationalEligibility != 0) & (locationalEligibility != 1)).any():
            raise ValueError('The locationEligibility entries have to be either 0 or 1.')
        # Check if given capacities indicate the same eligibility
        if capacityFix is not None:
            data = capacityFix.copy()
            data[data > 0] = 1
            if (data != locationalEligibility).any():
                raise ValueError('The locationEligibility and capacityFix parameters indicate different eligibilities.')
        if capacityMax is not None:
            data = capacityMax.copy()
            data[data > 0] = 1
            if (data != locationalEligibility).any():
                raise ValueError('The locationEligibility and capacityMax parameters indicate different eligibilities.')
        if capacityMin is not None:
            data = capacityMin.copy()
            data[data > 0] = 1
            if (data > locationalEligibility).any():
                raise ValueError('The locationEligibility and capacityMin parameters indicate different eligibilities.')
        if isBuiltFix is not None:
            if (isBuiltFix != locationalEligibility).any():
                raise ValueError('The locationEligibility and isBuiltFix parameters indicate different' +
                                 'eligibilities.')

    if isBuiltFix is not None:
        # Check if values are either one or zero
        if ((isBuiltFix != 0) & (isBuiltFix != 1)).any():
            raise ValueError('The isBuiltFix entries have to be either 0 or 1.')
        # Check if given capacities indicate the same design decisions
        if capacityFix is not None:
            data = capacityFix.copy()
            data[data > 0] = 1
            if (data > isBuiltFix).any():
                raise ValueError('The isBuiltFix and capacityFix parameters indicate different design decisions.')
        if capacityMax is not None:
            data = capacityMax.copy()
            data[data > 0] = 1
            if (data > isBuiltFix).any():
                warnings.warn('The isBuiltFix and capacityMax parameters indicate different design options.')
        if capacityMin is not None:
            data = capacityMin.copy()
            data[data > 0] = 1
            if (data > isBuiltFix).any():
                raise ValueError('The isBuiltFix and capacityMin parameters indicate different design decisions.')


def setLocationalEligibility(esM, locationalEligibility, capacityMax, capacityFix, isBuiltFix,
                             hasCapacityVariable, operationTimeSeries, dimension='1dim'):
    if locationalEligibility is not None:
        return locationalEligibility
    else:
        # If the location eligibility is None set it based on other information available
        if not hasCapacityVariable and operationTimeSeries is not None:
            if dimension == '1dim':
                data = operationTimeSeries.copy().sum()
                data[data > 0] = 1
                return data
            elif dimension == '2dim':
                data = operationTimeSeries.copy().sum()
                data.loc[:] = 1
                _locationalEligibility = data
                return _locationalEligibility
            else:
                raise ValueError("The dimension parameter has to be either \'1dim\' or \'2dim\' ")
        elif capacityFix is None and capacityMax is None and isBuiltFix is None:
            # If no information is given all values are set to 1
            if dimension == '1dim':
                return pd.Series([1 for loc in esM._locations], index=esM._locations)
            else:
                keys = {loc1 + '_' + loc2 for loc1 in esM._locations for loc2 in esM._locations if loc1 != loc2}
                return pd.Series([1 for key in keys], index=keys)
        elif isBuiltFix is not None:
            # If the isBuiltFix is not empty, the eligibility is set based on the fixed capacity
            data = isBuiltFix.copy()
            data[data > 0] = 1
            return data
        else:
            # If the fixCapacity is not empty, the eligibility is set based on the fixed capacity
            data = capacityFix.copy() if capacityFix is not None else capacityMax.copy()
            data[data > 0] = 1
            return data


def checkOperationTimeSeriesInputParameters(esM, operationTimeSeries, locationalEligibility, dimension='1dim'):
    if operationTimeSeries is not None:
        if not isinstance(operationTimeSeries, pd.DataFrame):
            raise TypeError('The operation time series data type has to be a pandas DataFrame')
        checkTimeSeriesIndex(esM, operationTimeSeries)

        if dimension == '1dim':
            checkRegionalColumnTitles(esM, operationTimeSeries)

            if locationalEligibility is not None and operationTimeSeries is not None:
                # Check if given capacities indicate the same eligibility
                data = operationTimeSeries.copy().sum()
                data[data > 0] = 1
                if (data > locationalEligibility).any().any():
                    raise ValueError('The locationEligibility and operationTimeSeries parameters indicate different' +
                                     ' eligibilities.')
        elif dimension == '2dim':
            keys = {loc1 + '_' + loc2 for loc1 in esM._locations for loc2 in esM._locations}
            columns = set(operationTimeSeries.columns)
            if not columns <= keys:
                raise ValueError('False column index detected in time series. ' +
                                 'The indicies have to be in the format \'loc1_loc2\' ' +
                                 'with loc1 and loc2 being locations in the energy system model.')

            for loc1 in esM._locations:
                for loc2 in esM._locations:
                    if loc1 + '_' + loc2 in columns and not loc2 + '_' + loc1 in columns:
                        raise ValueError('Missing data in time series DataFrame of a location connecting \n' +
                                         'component. If the flow is specified from loc1 to loc2, \n' +
                                         'then it must also be specified from loc2 to loc1.\n')

            if locationalEligibility is not None and operationTimeSeries is not None:
                # Check if given capacities indicate the same eligibility
                keys = set(locationalEligibility.index)
                if not columns == keys:
                    raise ValueError('The locationEligibility and operationTimeSeries parameters indicate different' +
                                     ' eligibilities.')

    if operationTimeSeries is not None and (operationTimeSeries < 0).any().any():
        raise ValueError('operationTimeSeries values smaller than 0 were detected.')


def checkDesignVariableModelingParameters(capacityVariableDomain, hasCapacityVariable, capacityPerPlantUnit,
                                          hasIsBuiltBinaryVariable, bigM):
    if capacityVariableDomain != 'continuous' and capacityVariableDomain != 'discrete':
        raise ValueError('The capacity variable domain has to be either \'continuous\' or \'discrete\'.')

    if not isinstance(hasIsBuiltBinaryVariable, bool):
        raise TypeError('The hasCapacityVariable variable domain has to be a boolean.')

    isStrictlyPositiveNumber(capacityPerPlantUnit)

    if not hasCapacityVariable and hasIsBuiltBinaryVariable:
        raise ValueError('To consider additional fixed cost contributions when installing\n' +
                         'capacities, capacity variables are required.')

    if bigM is None and hasIsBuiltBinaryVariable:
        raise ValueError('A bigM value needs to be specified when considering fixed cost contributions.')

    if bigM is not None:
        isinstance(bigM, bool)


def checkAndSetCostParameter(esM, name, data, dimension, locationEligibility):
    if dimension == '1dim':
        if not (isinstance(data, int) or isinstance(data, float) or isinstance(data, pd.Series)):
            raise TypeError('Type error in ' + name + ' detected.\n' +
                            'Economic parameters have to be a number or a pandas Series.')
    elif dimension == '2dim':
        if not (isinstance(data, int) or isinstance(data, float) or isinstance(data, pd.Series)):
            raise TypeError('Type error in ' + name + ' detected.\n' +
                            'Economic parameters have to be a number or a pandas Series.')
    else:
        raise ValueError("The dimension parameter has to be either \'1dim\' or \'2dim\' ")

    if dimension == '1dim':
        if isinstance(data, int) or isinstance(data, float):
            if data < 0:
                raise ValueError('Value error in ' + name + ' detected.\n Economic parameters have to be positive.')
            return pd.Series([float(data) for loc in esM._locations], index=esM._locations)
        checkRegionalIndex(esM, data)
    else:
        if isinstance(data, int) or isinstance(data, float):
            if data < 0:
                raise ValueError('Value error in ' + name + ' detected.\n Economic parameters have to be positive.')
            return pd.Series([float(data) for loc in locationEligibility.index], index=locationEligibility.index)
        checkConnectionIndex(data, locationEligibility)

    _data = data.astype(float)
    if _data.isnull().any():
        raise ValueError('Value error in ' + name + ' detected.\n' +
                         'An economic parameter contains values which are not numbers.')
    if (_data < 0).any():
        raise ValueError('Value error in ' + name + ' detected.\n' +
                         'All entries in economic parameter series have to be positive.')
    return _data


def checkClusteringInput(numberOfTypicalPeriods, numberOfTimeStepsPerPeriod, totalNumberOfTimeSteps):
    isStrictlyPositiveInt(numberOfTypicalPeriods), isStrictlyPositiveInt(numberOfTimeStepsPerPeriod)
    if not totalNumberOfTimeSteps % numberOfTimeStepsPerPeriod == 0:
        raise ValueError('The numberOfTimeStepsPerPeriod has to be an integer divisor of the total number of time\n' +
                         ' steps considered in the energy system model.')
    if totalNumberOfTimeSteps < numberOfTypicalPeriods * numberOfTimeStepsPerPeriod:
        raise ValueError('The product of the numberOfTypicalPeriods and the numberOfTimeStepsPerPeriod has to be \n' +
                         'smaller than the total number of time steps considered in the energy system model.')


def checkOptimizeInput(timeSeriesAggregation, isTimeSeriesDataClustered, logFileName, threads, solver,
                       timeLimit, optimizationSpecs, warmstart):
    if not isinstance(timeSeriesAggregation, bool):
        raise TypeError('The timeSeriesAggregation parameter has to be a boolean.')

    if timeSeriesAggregation and not isTimeSeriesDataClustered:
        raise ValueError('The time series flag indicates possible inconsistencies in the aggregated time series '
                         ' data.\n--> Call the cluster function first, then the optimize function.')

    if not isinstance(timeSeriesAggregation, bool):
        raise ValueError('The timeSeriesAggregation parameter has to be a boolean.')

    if not isinstance(logFileName, str):
        raise TypeError('The logFileName parameter has to be a string.')

    if not isinstance(threads, int) or threads < 0:
        raise TypeError('The threads parameter has to be a nonnegative integer.')

    if not isinstance(solver, str):
        raise TypeError('The solver parameter has to be a string.')

    if timeLimit is not None:
        isStrictlyPositiveNumber(timeLimit)

    if not isinstance(optimizationSpecs, str):
        raise TypeError('The optimizationSpecs parameter has to be a string.')

    if not isinstance(warmstart, bool):
        raise ValueError('The warmstart parameter has to be a boolean.')


def setFormattedTimeSeries(timeSeries):
    if timeSeries is None:
        return timeSeries
    else:
        data = timeSeries.copy()
        data["Period"], data["TimeStep"] = 0, data.index
        return data.set_index(['Period', 'TimeStep'])


def buildFullTimeSeries(df, periodsOrder):
    data = []
    for p in periodsOrder:
        data.append(df.loc[p])
    return pd.concat(data, axis=1, ignore_index=True)


def formatOptimizationOutput(data, varType, dimension, periodsOrder=None, compDict=None):
    # If data is an empty dictionary (because no variables of that type were declared) return None
    if not data:
        return None
    # If the dictionary is not empty, format it into a DataFrame
    if varType == 'designVariables' and dimension == '1dim':
        # Convert dictionary to DataFrame, transpose, put the components name first and sort the index
        # Results in a one dimensional DataFrame
        df = pd.DataFrame(data, index=[0]).T.swaplevel(i=0, j=1, axis=0).sort_index()
        # Unstack the regions (convert to a two dimensional DataFrame with the region indices being the columns)
        # and fill NaN values (i.e. when a component variable was not initiated for that region)
        df = df.unstack(level=-1)
        # Get rid of the unnecessary 0 level
        df.columns = df.columns.droplevel()
        return df
    elif varType == 'designVariables' and dimension == '2dim':
        # Convert dictionary to DataFrame, transpose, put the components name first while keeping the order of the
        # regions and sort the index
        # Results in a one dimensional DataFrame
        df = pd.DataFrame(data, index=[0]).T
        indexNew = []
        for tup in df.index.tolist():
            loc1, loc2 = compDict[tup[1]]._mapC[tup[0]]
            indexNew.append((loc1, loc2, tup[1]))
        df.index = pd.MultiIndex.from_tuples(indexNew)
        df = df.swaplevel(i=0, j=2, axis=0).swaplevel(i=1, j=2, axis=0).sort_index()
        # Unstack the regions (convert to a two dimensional DataFrame with the region indices being the columns)
        # and fill NaN values (i.e. when a component variable was not initiated for that region)
        df = df.unstack(level=-1)
        # Get rid of the unnecessary 0 level
        df.columns = df.columns.droplevel()
        return df
    elif varType == 'operationVariables' and dimension == '1dim':
        # Convert dictionary to DataFrame, transpose, put the period column first and sort the index
        # Results in a one dimensional DataFrame
        df = pd.DataFrame(data, index=[0]).T.swaplevel(i=0, j=-2).sort_index()
        # Unstack the time steps (convert to a two dimensional DataFrame with the time indices being the columns)
        df = df.unstack(level=-1)
        # Get rid of the unnecessary 0 level
        df.columns = df.columns.droplevel()
        # Re-engineer full time series by using Pandas' concat method (only one loop if time series aggregation was not
        # used)
        return buildFullTimeSeries(df, periodsOrder)
    elif varType == 'operationVariables' and dimension == '2dim':
        # Convert dictionary to DataFrame, transpose, put the period column first while keeping the order of the
        # regions and sort the index
        # Results in a one dimensional DataFrame
        df = pd.DataFrame(data, index=[0]).T
        indexNew = []
        for tup in df.index.tolist():
            loc1, loc2 = compDict[tup[1]]._mapC[tup[0]]
            indexNew.append((loc1, loc2, tup[1], tup[2], tup[3]))
        df.index = pd.MultiIndex.from_tuples(indexNew)
        df = df.swaplevel(i=1, j=2, axis=0).swaplevel(i=0, j=3, axis=0).swaplevel(i=2, j=3, axis=0).sort_index()
        # Unstack the time steps (convert to a two dimensional DataFrame with the time indices being the columns)
        df = df.unstack(level=-1)
        # Get rid of the unnecessary 0 level
        df.columns = df.columns.droplevel()
        # Re-engineer full time series by using Pandas' concat method (only one loop if time series aggregation was not
        # used)
        return buildFullTimeSeries(df, periodsOrder)
    else:
        raise ValueError('The varType parameter has to be either \'designVariables\' or \'operationVariables\'\n' +
                         'and the dimension parameter has to be either \'1dim\' or \'2dim\'.')


def setOptimalComponentVariables(optVal, varType, compDict):
    if optVal is not None:
        for compName, comp in compDict.items():
            if compName in optVal.index:
                setattr(comp, varType, optVal.loc[compName])
            else:
                setattr(comp, varType, None)


def preprocess2dimData(data, mapC=None):
    if data is not None and isinstance(data, pd.DataFrame):
        if mapC is None:
            index, data_ = [], []
            for loc1 in data.index:
                for loc2 in data.columns:
                    if data[loc1][loc2] > 0:
                        index.append(loc1 + '_' + loc2), data_.append(data[loc1][loc2])
            return pd.Series(data_, index=index)
        else:
            return pd.Series(mapC).apply(lambda loc: data[loc[0]][loc[1]])
    else:
        return data


def map2dimData(data, mapC):
    if data is not None and isinstance(data, pd.DataFrame):
        return pd.Series(mapC).apply(lambda loc: data[loc[0]][loc[1]])
    else:
        return data
