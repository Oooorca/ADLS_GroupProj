#!/usr/bin/env python3

# This script tests the fixed point linear
import os, logging

import cocotb
from cocotb.log import SimLog
from cocotb.triggers import *

from mase_cocotb.testbench import Testbench
from mase_cocotb.interfaces.streaming import (
    MultiSignalStreamDriver,
    MultiSignalStreamMonitor,
)
from mase_cocotb.runner import mase_runner
from utils import mxint_quantize

import torch

logger = logging.getLogger("testbench")
logger.setLevel(logging.DEBUG)


class MXINTVectorMultTB(Testbench):
    def __init__(self, dut, num) -> None:
        super().__init__(dut, dut.clk, dut.rst)
        self.num = num
        if not hasattr(self, "log"):
            self.log = SimLog("%s" % (type(self).__qualname__))

        self.data_in_0_driver = MultiSignalStreamDriver(
            dut.clk,
            (dut.mdata_in_0, dut.edata_in_0),
            dut.data_in_0_valid,
            dut.data_in_0_ready,
        )
        self.weight_driver = MultiSignalStreamDriver(
            dut.clk,
            (dut.mweight, dut.eweight),
            dut.weight_valid,
            dut.weight_ready,
        )

        self.data_out_0_monitor = MultiSignalStreamMonitor(
            dut.clk,
            (dut.mdata_out_0, dut.edata_out_0),
            dut.data_out_0_valid,
            dut.data_out_0_ready,
            check=True,
        )
        self.data_in_0_driver.log.setLevel(logging.DEBUG)
        self.weight_driver.log.setLevel(logging.DEBUG)
        self.data_out_0_monitor.log.setLevel(logging.DEBUG)

    def generate_inputs(self):
        inputs = []
        weights = []
        exp_outputs = []
        for _ in range(self.num):
            data = 20 * torch.rand(int(self.dut.BLOCK_SIZE))
            (data_in, mdata_in, edata_in) = mxint_quantize(
                data,
                int(self.dut.DATA_IN_0_PRECISION_0),
                int(self.dut.DATA_IN_0_PRECISION_1),
            )
            w = 20 * torch.rand(int(self.dut.BLOCK_SIZE))

            (weight, mweight, eweight) = mxint_quantize(
                w,
                int(self.dut.WEIGHT_PRECISION_0),
                int(self.dut.WEIGHT_PRECISION_1),
            )
            exp_out, mexp_out, eexp_out = mxint_quantize(
                data_in * weight,
                int(self.dut.DATA_OUT_0_PRECISION_0),
                int(self.dut.DATA_OUT_0_PRECISION_1),
                edata_in + eweight,
            )
            inputs.append((mdata_in.int().tolist(), edata_in.int().tolist()))
            weights.append((mweight.int().tolist(), eweight.int().tolist()))
            exp_outputs.append((mexp_out.int().tolist(), eexp_out.int().tolist()))
        return inputs, weights, exp_outputs

    async def run_test(self):
        await self.reset()
        logger.info(f"Reset finished")
        self.data_out_0_monitor.ready.value = 1

        logger.info(f"generating inputs")
        inputs, weights, exp_outputs = self.generate_inputs()

        # Load the inputs driver
        self.data_in_0_driver.load_driver(inputs)
        self.weight_driver.load_driver(weights)

        # Load the output monitor
        self.data_out_0_monitor.load_monitor(exp_outputs)

        await Timer(5, units="us")
        assert self.data_out_0_monitor.exp_queue.empty()


@cocotb.test()
async def test(dut):
    tb = MXINTVectorMultTB(dut, num=20)
    await tb.run_test()


if __name__ == "__main__":
    mase_runner(
        trace=True,
        module_param_list=[
            {
                "DATA_IN_0_PRECISION_0": 8,
                "DATA_IN_0_PRECISION_1": 4,
                "WEIGHT_PRECISION_0": 12,
                "WEIGHT_PRECISION_1": 4,
                "BLOCK_SIZE": 4,
            },
            # {
            #     "DATA_IN_0_PRECISION_0": 8,
            #     "DATA_IN_0_PRECISION_1": 4,
            #     "WEIGHT_PRECISION_0": 8,
            #     "WEIGHT_PRECISION_1": 4,
            #     "BLOCK_SIZE": 4,
            # },
            # {
            #     "DATA_IN_0_PRECISION_0": 8,
            #     "DATA_IN_0_PRECISION_1": 4,
            #     "WEIGHT_PRECISION_0": 8,
            #     "WEIGHT_PRECISION_1": 4,
            #     "BLOCK_SIZE": 4,
            # },
        ],
    )
