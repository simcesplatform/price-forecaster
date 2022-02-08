# -*- coding: utf-8 -*-
# Copyright 2021 Tampere University and VTT Technical Research Centre of Finland
# This software was developed as a part of the ProCemPlus project: https://www.senecc.fi/projects/procemplus
# This source code is licensed under the MIT license. See LICENSE in the repository root directory.
# Author(s): Amir Safdarian <amir.safdarian@vtt.fi>
'''
Contains classes related to reading price forecast state from a csv file.
'''
from dataclasses import dataclass

import csv

@dataclass
class PriceForecastState():
    '''
    Represents price forecast state read from the csv file.
    ''' 
    
    market_id: str
    unit_of_measure: str
    timedata: list
    pricedata: list
    resource_id: str = None
    pricing_type: str = None
    

class CsvFileError(Exception):
    '''
    CsvFilePriceStateSource was unable to read the given csv file or the file was missing a required column.
    '''    

class NoDataAvailableForEpoch( Exception ):
    """Raised by CsvFileResourceDataSource.getNextEpochData when there is no more PriceForecastStates available from the csv file."""

class CsvFilePriceStateSource():
    '''
    Class for getting price forecast states from a csv file.
    '''
    
    def __init__(self, file_name: str, delimiter: str = ","  ):
        '''
        Creates object which uses the given csv file that uses the given delimiter.
        Raises CsvFileError if file cannot be read e.g. file not found, or it is missing required columns.
        '''
        self._file = None # required if there is no file and the __del__ method is executed
        try:
            self._file = open( file_name, newline = "")
            
        except Exception as e:
            raise CsvFileError( f'Unable to read file {file_name}: {str( e )}.' )
        
        self._csv = csv.DictReader( self._file, delimiter = delimiter )
        # check that self._csv.fieldnames has required fields
        required_fields = set( [ 'MarketId', 'UnitOfMeasure', 'Time1', 'Price1'])
        fields = set( self._csv.fieldnames )
        # missing contains fields that do not exist or is empty if all fields exist.
        missing = required_fields.difference( fields )
        if len( missing ) > 0:
            raise CsvFileError( f'Price forecast state source csv file missing required columns: {",".join( missing )}.' )
        
    def __del__(self):
        '''
        Close the csv file when this object is destroyed.
        '''
        if self._file != None:
            self._file.close()
        
    def getNextEpochData(self) -> PriceForecastState:
        '''
        Gets price forecast state for the next epoch i.e. read the next csv file row and return its contents.
        Raises NoDataAvailableForEpoch if the csv file has no more rows.
        Raises ValueError if a value from the csv file cannot be converted to the appropriate data type e.g. Prices value to float.
        '''
        try:
            row = next( self._csv )
            
        except StopIteration:
            raise NoDataAvailableForEpoch( 'The source csv file does not have any rows remaining.' )
        
        # validation info for each column: column name, corresponding PriceForecastState attribute, python type used in conversion
        # and are None values accepted including converting an empty string to None
        validation_info = [
            ( 'MarketId', 'market_id', str, False ),
            ( 'UnitOfMeasure', 'unit_of_measure', str, False ),
            ( 'ResourceId', 'resource_id', str, True ),
            ( 'PricingType', 'pricing_type', str, True )
        ]
        
        values = {} # values for PriceForecastState attributes
        for column, attr, dataType, canBeNone in validation_info:
            value = row.get( column )
            row.pop(column)
            if canBeNone and value == None:
                # ResourceId and PricingType can have None since presence of other fields is checked in init_tools
                values[attr] = None
                    
            elif canBeNone and value == '': 
                # convert empty string to None
                values[attr] = None
                
            else:
                try:
                    # try conversion to correct data type
                    values[attr] = dataType( value )
                    
                except ValueError:
                    raise ValueError( f'Value "{value}" in csv column {column} cannot be converted to {dataType.__name__}' ) 

        # no_interval is the number of time intervals for which time stamp and price data are provided in the csv file. It is assumed
        # that in the row, all other data are removed and we only have price abd timestamp data 
        no_interval = int(len(row)/2)
        timedata_list = []
        pricedata_list = []

        
        for i in range(no_interval):
            timeind='Time'+str(i+1)
            priceind='Price'+str(i+1)
            timedata_list.append(row[timeind])
            pricedata_list.append(row[priceind])
        
        values['timedata']=timedata_list
        values['pricedata']=pricedata_list        
        
        state = PriceForecastState( **values )

        return state
