`timescale 1ns / 1ps
// Join synchronises n sets of input handshake signals with a set of output handshaked signals
module join_n #(
    parameter NUM_HANDSHAKES = 4
) (
    input logic [NUM_HANDSHAKES-1:0] data_in_valid,
    output logic [NUM_HANDSHAKES-1:0] data_in_ready,
    output logic data_out_valid,
    input logic data_out_ready
);

  generate
    if (NUM_HANDSHAKES == 1) begin : gen_passthrough
      assign data_out_valid   = data_in_valid[0];
      assign data_in_ready[0] = data_out_ready;
    end else begin : gen_join_handshake
      logic [NUM_HANDSHAKES-1:0] all_valid;
      // If only some of the inputs are valid - we need to stall those inputs and wait
      // for the other inputs by setting some of the ready bits to 0.
      // Example with 3 handshakes:
      // +-----------+-----------+------------+------------+------------+------------+------------+
      // | out_ready |in_valid_0 | in_valid_1 | in_valid_2 | in_ready_0 | in_ready_1 | in_ready_2 |
      // +-----------+-----------+------------+------------+------------+------------+------------+
      // |         0 |         0 |          0 |          0 |          0 |          0 |          0 |
      // +-----------+-----------+------------+------------+------------+------------+------------+
      // |         0 |         0 |          0 |          1 |          0 |          0 |          0 |
      // +-----------+-----------+------------+------------+------------+------------+------------+
      // |         0 |         0 |          1 |          0 |          0 |          0 |          0 |
      // +-----------+-----------+------------+------------+------------+------------+------------+
      // |         0 |         0 |          1 |          1 |          0 |          0 |          0 |
      // +-----------+-----------+------------+------------+------------+------------+------------+
      // |         0 |         1 |          0 |          0 |          0 |          0 |          0 |
      // +-----------+-----------+------------+------------+------------+------------+------------+
      // |         0 |         1 |          0 |          1 |          0 |          0 |          0 |
      // +-----------+-----------+------------+------------+------------+------------+------------+
      // |         0 |         1 |          1 |          0 |          0 |          0 |          0 |
      // +-----------+-----------+------------+------------+------------+------------+------------+
      // |         0 |         1 |          1 |          1 |          0 |          0 |          0 |
      // +-----------+-----------+------------+------------+------------+------------+------------+
      // |         1 |         0 |          0 |          0 |          1 |          1 |          1 |
      // +-----------+-----------+------------+------------+------------+------------+------------+
      // |         1 |         0 |          0 |          1 |          1 |          1 |          0 |
      // +-----------+-----------+------------+------------+------------+------------+------------+
      // |         1 |         0 |          1 |          0 |          1 |          0 |          1 |
      // +-----------+-----------+------------+------------+------------+------------+------------+
      // |         1 |         0 |          1 |          1 |          1 |          0 |          0 |
      // +-----------+-----------+------------+------------+------------+------------+------------+
      // |         1 |         1 |          0 |          0 |          0 |          1 |          1 |
      // +-----------+-----------+------------+------------+------------+------------+------------+
      // |         1 |         1 |          0 |          1 |          0 |          1 |          0 |
      // +-----------+-----------+------------+------------+------------+------------+------------+
      // |         1 |         1 |          1 |          0 |          0 |          0 |          1 |
      // +-----------+-----------+------------+------------+------------+------------+------------+
      // |         1 |         1 |          1 |          1 |          1 |          1 |          1 |
      // +-----------+-----------+------------+------------+------------+------------+------------+

      assign all_valid = &data_in_valid;
      always_comb begin
        for (int i = 0; i < NUM_HANDSHAKES; i++) begin
          if (all_valid) begin
            // Every data input is valid. We're ready to recieve as long as
            // the output is also ready!
            data_in_ready[i] = data_out_ready;
          end else begin
            // Some data inputs are not valid. Indicate we are ready to recieve
            // for these inputs, while stalling the ones that are ready.
            data_in_ready[i] = data_out_ready & (!data_in_valid[i]);
          end
        end
      end

      assign data_out_valid = all_valid;
    end
  endgenerate

endmodule
