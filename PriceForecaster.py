# -*- coding: utf-8 -*-
# Copyright 2021 Tampere University and VTT Technical Research Centre of Finland
# This software was developed as a part of the ProCemPlus project: https://www.senecc.fi/projects/procemplus
# This source code is licensed under the MIT license. See LICENSE in the repository root directory.
# Author(s): Amir Safdarian <amir.safdarian@vtt.fi>
import init
import asyncio

from tools.components import AbstractSimulationComponent
from tools.tools import FullLogger, load_environmental_variables
from tools.message.block import ValueArrayBlock, TimeSeriesBlock
from domain_messages.price_forecaster.price_forecast import PriceForecastStateMessage
from price_forecaster_state_source.price_forecast_state_source  import CsvFilePriceStateSource, CsvFileError


# names of used environment variables
PRICE_FORECASTER_STATE_CSV_FILE = "PRICE_FORECASTER_STATE_CSV_FILE"
PRICE_FORECASTER_STATE_CSV_DELIMITER = "PRICE_FORECASTER_STATE_CSV_DELIMITER"
PRICE_FORECAST_STATE_TOPIC = "PRICE_FORECAST_STATE_TOPIC"


LOGGER = FullLogger( __name__ )


class PriceForecaster(AbstractSimulationComponent):

    def __init__(self, stateSource: CsvFilePriceStateSource, initialization_error = None ):

        super().__init__()
        self._stateSource = stateSource
        self.initialization_error = initialization_error
        if self._stateSource is None and self.initialization_error is None:
            self.initialization_error = 'Did not receive a csv file.'

        environment = load_environmental_variables(
            (PRICE_FORECAST_STATE_TOPIC, str, "PriceForecastState")
            )

        if self.initialization_error != None:
            LOGGER.error( self.initialization_error )

        self._price_forecast_state_topic = environment[ PRICE_FORECAST_STATE_TOPIC ]
        self._topic = '.'.join([ self._price_forecast_state_topic])

    async def process_epoch(self) -> bool:

        LOGGER.debug( 'Starting epoch.' )

        try:
            await self._send_PriceForecast_state_message()

        except Exception as error:
            description = f'Unable to create or send a PriceForecasterState message: {str( error )}'
            LOGGER.error( description )
            await self.send_error_message(description)
            return False

        return True
    
    async def _send_PriceForecast_state_message(self):
        priceforecaststate = self._get_PriceForecast_state_message()

        #state = self._stateSource.getCurrentEpochData()

        #self._result_topic = '.'.join( [ self._result_topic, state.market_id, state.resource_id])
        await self._rabbitmq_client.send_message(self._result_topic, priceforecaststate.bytes())

    def _get_PriceForecast_state_message(self) -> PriceForecastStateMessage:
        state = self._stateSource.getNextEpochData()
        self._result_topic = '.'.join( [ self._topic, state.market_id, state.resource_id])
        prices=TimeSeriesBlock(
            TimeIndex=state.timedata,
            Series={
                "Price": ValueArrayBlock(
                    UnitOfMeasure=state.unit_of_measure,
                    Values=state.pricedata
                    )
                }
            )
        message = PriceForecastStateMessage(
            SimulationId = self.simulation_id,
            Type = PriceForecastStateMessage.CLASS_MESSAGE_TYPE,
            SourceProcessId = self.component_name,
            MessageId = next(self._message_id_generator),
            EpochNumber = self._latest_epoch,
            TriggeringMessageIds = self._triggering_message_ids,
            MarketId = state.market_id,
            Prices = prices,
            ResourceId = state.resource_id,
            PricingType = state.pricing_type
            )
        return message

def create_component() -> PriceForecaster:
    environment = load_environmental_variables(
        ( PRICE_FORECASTER_STATE_CSV_FILE, str ),
        ( PRICE_FORECASTER_STATE_CSV_DELIMITER, str, "," )
        )
    try:
        stateSource = CsvFilePriceStateSource( environment[PRICE_FORECASTER_STATE_CSV_FILE], environment[PRICE_FORECASTER_STATE_CSV_DELIMITER])
        initialization_error = None
    except CsvFileError as error:
        stateSource = None
        initialization_error = f'Unable to create a csv file for the component: {str( error )}'

    return PriceForecaster(stateSource, initialization_error )

async def start_component():
    PriceForecaster = create_component()
    await PriceForecaster.start()
    while not PriceForecaster.is_stopped:
        await asyncio.sleep( 2 )

if __name__ == '__main__':
    asyncio.run(start_component())






