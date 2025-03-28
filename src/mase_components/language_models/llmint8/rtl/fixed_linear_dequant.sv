`timescale 1ns / 1ps

/*
 * Constrained by WEIGHT_PARALLELISM_DIM_0 == DATA_OUT_0_PARALLELISM_DIM_0
 *
*/

module fixed_linear_dequant #(
    /* verilator lint_off UNUSEDPARAM */
    parameter HAS_BIAS = 0,

    parameter DATA_IN_0_PRECISION_0 = 8,
    parameter DATA_IN_0_PRECISION_1 = 0,
    parameter DATA_IN_0_TENSOR_SIZE_DIM_0 = 4,
    parameter DATA_IN_0_TENSOR_SIZE_DIM_1 = 1,
    parameter DATA_IN_0_PARALLELISM_DIM_0 = 4,
    parameter DATA_IN_0_PARALLELISM_DIM_1 = 1,
    parameter IN_0_DEPTH = DATA_IN_0_TENSOR_SIZE_DIM_0 / DATA_IN_0_PARALLELISM_DIM_0,

    parameter WEIGHT_PRECISION_0 = 8,
    parameter WEIGHT_PRECISION_1 = 0,
    parameter WEIGHT_TENSOR_SIZE_DIM_0 = 32,
    parameter WEIGHT_TENSOR_SIZE_DIM_1 = 1,
    parameter WEIGHT_PARALLELISM_DIM_0 = 4,
    parameter WEIGHT_PARALLELISM_DIM_1 = 1,

    parameter DATA_OUT_0_PRECISION_0 = DATA_IN_0_PRECISION_0 + WEIGHT_PRECISION_0 + $clog2(
        DATA_IN_0_TENSOR_SIZE_DIM_0
    ) + $clog2(
        IN_0_DEPTH
    ) + HAS_BIAS,
    parameter DATA_OUT_0_PRECISION_1 = DATA_IN_0_PRECISION_1 + WEIGHT_PRECISION_1,
    parameter DATA_OUT_0_TENSOR_SIZE_DIM_0 = 4,
    parameter DATA_OUT_0_TENSOR_SIZE_DIM_1 = 1,
    parameter DATA_OUT_0_PARALLELISM_DIM_0 = WEIGHT_PARALLELISM_DIM_0,
    parameter DATA_OUT_0_PARALLELISM_DIM_1 = 1,

    parameter BIAS_PRECISION_0 = 8,
    parameter BIAS_PRECISION_1 = 0,
    parameter BIAS_TENSOR_SIZE_DIM_0 = DATA_OUT_0_TENSOR_SIZE_DIM_0,
    parameter BIAS_TENSOR_SIZE_DIM_1 = 1,
    parameter BIAS_PARALLELISM_DIM_0 = WEIGHT_PARALLELISM_DIM_0,
    parameter BIAS_PARALLELISM_DIM_1 = 1,

    parameter DEQUANTIZATION_WIDTH = 16,
    parameter MAX_NUM_WIDTH = 16
) (
    input clk,
    input rst,

    // input port for data_inivations
    input  [DATA_IN_0_PRECISION_0-1:0] data_in_0      [DATA_IN_0_PARALLELISM_DIM_0*DATA_IN_0_PARALLELISM_DIM_1-1:0],
    input [MAX_NUM_WIDTH-1:0] data_in_0_max_num,  // obtained from quantizer
    input data_in_0_valid,
    output data_in_0_ready,

    // input port for weight
    input  [WEIGHT_PRECISION_0-1:0] weight      [WEIGHT_PARALLELISM_DIM_0 * DATA_IN_0_PARALLELISM_DIM_0-1:0],
    input [MAX_NUM_WIDTH-1:0] weight_max_num,  // obtained from quantizer
    input weight_valid,
    output weight_ready,

    /* verilator lint_off UNUSEDSIGNAL */
    input [BIAS_PRECISION_0-1:0] bias[BIAS_PARALLELISM_DIM_0 * DATA_OUT_0_PARALLELISM_DIM_1-1:0],
    input bias_valid,
    /* verilator lint_on UNUSEDSIGNAL */
    output bias_ready,

    output [DATA_OUT_0_PRECISION_0-1:0] data_out_0      [DATA_OUT_0_PARALLELISM_DIM_0*DATA_OUT_0_PARALLELISM_DIM_1-1:0],
    output data_out_0_valid,
    input data_out_0_ready
);

  localparam FDP_WIDTH = DATA_IN_0_PRECISION_0 + WEIGHT_PRECISION_0 + $clog2(
      DATA_IN_0_PARALLELISM_DIM_0
  );
  //   localparam ACC_WIDTH = FDP_WIDTH + $clog2(IN_0_DEPTH);  
  localparam FDP_DEQUANT_WIDTH = DATA_OUT_0_PRECISION_0;  //TODO: overflow & rounding?
  localparam ACC_WIDTH = DATA_OUT_0_PRECISION_0;  // TODO

  logic fdp_join_valid, fdp_join_ready;
  join2 #() fdp_join_inst (
      .data_in_ready ({weight_ready, data_in_0_ready}),
      .data_in_valid ({weight_valid, data_in_0_valid}),
      .data_out_valid(fdp_join_valid),
      .data_out_ready(fdp_join_ready)
  );

  /* verilator lint_off UNUSEDSIGNAL */
  // Assume the parallelised hardware above have the same arrival time
  // which means that they always have the same state. So we can just
  // pick one of the valid signal to use.
  logic [WEIGHT_PARALLELISM_DIM_0-1:0] fdp_data_ready, fdp_weight_ready;
  assign fdp_join_ready = fdp_data_ready[0];
  /* verilator lint_on UNUSEDSIGNAL */

  logic                 acc_ready;
  logic [ACC_WIDTH-1:0] acc_data_out[WEIGHT_PARALLELISM_DIM_0*WEIGHT_PARALLELISM_DIM_1-1:0];

  // There are WEIGHT_PARALLELISM_DIM_0 number of dot product instances with DATA_IN_0_TENSOR_SIZE_DIM_0 inputs
  // and each one computes for IN_0_DEPTH iterations for each inputs.
  for (genvar i = 0; i < WEIGHT_PARALLELISM_DIM_0; i = i + 1) begin : linear
    // Assume the weight are transposed and partitioned 
    logic [WEIGHT_PRECISION_0-1:0] current_weight[DATA_IN_0_PARALLELISM_DIM_0-1:0];
    assign current_weight = weight[DATA_IN_0_PARALLELISM_DIM_0*(i+1)-1:DATA_IN_0_PARALLELISM_DIM_0*i];

    logic [FDP_WIDTH-1:0] fdp_data_out;
    logic fdp_data_out_valid, fdp_data_out_ready;

    // The inputs are already sync-ed by the previous join
    fixed_dot_product #(
        .IN_WIDTH(DATA_IN_0_PRECISION_0),
        .WEIGHT_WIDTH(WEIGHT_PRECISION_0),
        .IN_SIZE(DATA_IN_0_PARALLELISM_DIM_0)
    ) fdp_inst (
        .clk(clk),
        .rst(rst),
        .data_in(data_in_0),
        .data_in_valid(fdp_join_valid),
        .data_in_ready(fdp_data_ready[i]),
        .weight(current_weight),
        .weight_valid(fdp_join_valid),
        .weight_ready(fdp_weight_ready[i]),
        .data_out(fdp_data_out),
        .data_out_valid(fdp_data_out_valid),
        .data_out_ready(fdp_data_out_ready)
    );


    /******* Dequantization*******/
    // TODO: dequantizer vs. dequantizer_single?
    // Reshape input and output data of dequantizer to fit in the module port format
    logic [FDP_WIDTH-1:0] fdp_data_out_array[0:0];
    logic [FDP_DEQUANT_WIDTH-1:0] fdp_dequant_out_array[0:0];
    assign fdp_data_out_array[0] = fdp_data_out;
    assign fdp_dequant_out = fdp_dequant_out_array[0];

    logic dequantizer_in_valid, dequantizer_in_ready;
    logic max_num_buffered_valid;
    assign max_num_buffered_valid = max_num_buffered_valid_join;  // broadcast valid siganl from the shared FIFO
    /* verilator lint_off UNUSEDSIGNAL */
    logic max_num_buffered_ready;
    join2 #() dequant_join (
        .data_in_valid ({max_num_buffered_valid, fdp_data_out_valid}),
        .data_in_ready ({max_num_buffered_ready, fdp_data_out_ready}),
        .data_out_valid(dequantizer_in_valid),
        .data_out_ready(dequantizer_in_ready)
    );
    logic [FDP_DEQUANT_WIDTH-1:0] fdp_dequant_out;

    logic fdp_dequant_out_valid, fdp_dequant_out_ready;
    dequantizer #(
        .IN_WIDTH(FDP_WIDTH),
        .IN_SIZE(1),  // only one entry
        .IN_PARALLELISM(1),  // only one entry
        .OUT_WIDTH(ACC_WIDTH),
        .MAX_NUM_WIDTH(TOTAL_MAX_NUM_WIDTH),
        .QUANTIZATION_WIDTH(DEQUANTIZATION_WIDTH)
    ) dequant_inst (
        .clk(clk),
        .rst(rst),
        .data_in(fdp_data_out_array),
        .data_in_valid(dequantizer_in_valid),
        .data_in_ready(dequantizer_in_ready),
        .max_num(max_num_buffered),
        .data_out(fdp_dequant_out_array),
        .data_out_valid(fdp_dequant_out_valid),
        .data_out_ready(fdp_dequant_out_ready)
    );
    /************************ End of Dequantization ******************/

    /* verilator lint_off UNUSEDSIGNAL */
    logic acc_data_out_valid, acc_data_out_ready;
    /* verilator lint_on UNUSEDSIGNAL */

    fixed_accumulator #(
        .IN_WIDTH(FDP_DEQUANT_WIDTH),
        .IN_DEPTH(IN_0_DEPTH)
    ) fixed_accumulator_inst (
        .clk(clk),
        .rst(rst),
        .data_in(fdp_dequant_out),
        .data_in_valid(fdp_dequant_out_valid),
        .data_in_ready(fdp_dequant_out_ready),
        .data_out(acc_data_out[i]),
        .data_out_valid(acc_data_out_valid),
        .data_out_ready(acc_data_out_ready)
    );

    // Assume the parallelised hardware above have the same arrival time
    // which means that they always have the same state. So we can just
    // pick one of the valid signal to use.
    assign acc_data_out_ready = acc_ready;
  end

  /******* max num multiplication & FIFO buffering *******/
  localparam TOTAL_MAX_NUM_WIDTH = 2*MAX_NUM_WIDTH + 1;  // purposely leave one more bit to prevent overflow
  logic [TOTAL_MAX_NUM_WIDTH-1:0] max_num;
  fixed_mult #(
      .IN_A_WIDTH(MAX_NUM_WIDTH),
      .IN_B_WIDTH(MAX_NUM_WIDTH)
  ) max_num_mult_inst (
      .data_a (data_in_0_max_num),
      .data_b (weight_max_num),
      .product(max_num)
  );

  logic [TOTAL_MAX_NUM_WIDTH-1:0] max_num_buffered;
  logic max_num_buffered_ready_join, max_num_buffered_valid_join;
  // Assume the parallelised FDP and ACC module in "linear" loop always have 
  // the same valid & ready state, so we can just pick one of the ready signal to use.
  assign max_num_buffered_ready_join = linear[0].max_num_buffered_ready;
  localparam FMM_DELAY = DATA_IN_0_PARALLELISM_DIM_0 * 10;  //TODO: fifo depth too large?

  /* verilator lint_off PINMISSING */
  fifo #(
      .DEPTH(FMM_DELAY + 1),
      .DATA_WIDTH(TOTAL_MAX_NUM_WIDTH)
  ) data_in_fifo_inst (
      .clk(clk),
      .rst(rst),
      .in_data(max_num),
      .in_valid(data_in_0_valid),  //TODO: assume din1_max_num & din2_max_num arrive in sync
      //   .in_ready (fifo_in_ready),
      .out_data(max_num_buffered),
      .out_valid(max_num_buffered_valid_join),
      .out_ready(max_num_buffered_ready_join)
  );







  if (HAS_BIAS == 1) begin
    logic [ACC_WIDTH-1:0] bias_sext[BIAS_PARALLELISM_DIM_0 * DATA_IN_0_PARALLELISM_DIM_1-1:0];
    logic acc_join_valid, acc_join_ready;
    logic [BIAS_PARALLELISM_DIM_0-1:0] reg_ready;

    join2 #() acc_join_inst (
        .data_in_ready ({bias_ready, acc_ready}),
        .data_in_valid ({bias_valid, linear[0].acc_data_out_valid}),
        .data_out_valid(acc_join_valid),
        .data_out_ready(acc_join_ready)
    );

    fixed_rounding #(
        .IN_SIZE(BIAS_PARALLELISM_DIM_0 * DATA_IN_0_PARALLELISM_DIM_1),
        .IN_WIDTH(BIAS_PRECISION_0),
        .IN_FRAC_WIDTH(BIAS_PRECISION_1),
        .OUT_WIDTH(ACC_WIDTH),
        .OUT_FRAC_WIDTH(DATA_IN_0_PRECISION_1 + WEIGHT_PRECISION_1)
    ) bias_cast (
        .data_in (bias),
        .data_out(bias_sext)
    );

    assign acc_join_ready = &reg_ready;

    for (genvar i = 0; i < WEIGHT_PARALLELISM_DIM_0; i = i + 1) begin : add_bias
      logic [DATA_OUT_0_PRECISION_0-1:0] add;
      assign add = $signed(acc_data_out[i]) + $signed(bias_sext[i]);
      /* verilator lint_off UNUSEDSIGNAL */
      logic dout_valid;
      skid_buffer #(
          .DATA_WIDTH(DATA_OUT_0_PRECISION_0)
      ) register_slice (
          .clk           (clk),
          .rst           (rst),
          .data_in_valid (acc_join_valid),
          .data_in_ready (reg_ready[i]),
          .data_in       (add),
          .data_out_valid(dout_valid),
          .data_out_ready(data_out_0_ready),
          .data_out      (data_out_0[i])
      );
    end
    assign data_out_0_valid = add_bias[0].dout_valid;

  end else begin
    assign acc_ready = data_out_0_ready;
    assign data_out_0_valid = linear[0].acc_data_out_valid;

    for (genvar i = 0; i < WEIGHT_PARALLELISM_DIM_0; i = i + 1) begin
      assign data_out_0[i] = acc_data_out[i];
    end
    assign bias_ready = 1;
  end

endmodule
