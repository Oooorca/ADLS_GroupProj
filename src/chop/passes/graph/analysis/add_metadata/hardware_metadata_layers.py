# mase_op : the set of functional equivalent IPs with different design configurations.
# The first IP in each list is used by default
norm = {
    "name": "norm",
    "dependence_files": [
        "common/rtl/join2.sv",
        "common/rtl/split2.sv",
        "common/rtl/register_slice.sv",
        "common/rtl/lut.sv",
        "memory/rtl/simple_dual_port_ram.sv",
        "memory/rtl/repeat_circular_buffer.sv",
        "memory/rtl/fifo.sv",
        "memory/rtl/skid_buffer.sv",
        "cast/rtl/floor_round.sv",
        "cast/rtl/signed_clamp.sv",
        "cast/rtl/fixed_signed_cast.sv",
        "linear_layers/fixed_operators/rtl/fixed_accumulator.sv",
        "linear_layers/fixed_operators/rtl/fixed_adder_tree.sv",
        "linear_layers/fixed_operators/rtl/fixed_adder_tree_layer.sv",
        "linear_layers/fixed_operators/rtl/fixed_lut_index.sv",
        "linear_layers/fixed_operators/rtl/fixed_range_augmentation.sv",
        "linear_layers/fixed_operators/rtl/fixed_range_reduction.sv",
        "scalar_operators/fixed/rtl/fixed_isqrt.sv",
        "scalar_operators/fixed/rtl/fixed_nr_stage.sv",
        "linear_layers/matmul/rtl/matrix_fifo.sv",
        "linear_layers/matmul/rtl/matrix_flatten.sv",
        "linear_layers/matmul/rtl/matrix_unflatten.sv",
        "normalization_layers/rtl/channel_selection.sv",
        "normalization_layers/rtl/group_norm_2d.sv",
        "normalization_layers/rtl/rms_norm_2d.sv",
        "normalization_layers/rtl/batch_norm_2d.sv",
        "normalization_layers/rtl/norm.sv",
    ],
}

INTERNAL_COMP = {
    "linear": [
        {
            "name": "fixed_linear",
            "dependence_files": [
                "cast/rtl/fixed_cast.sv",
                "linear_layers/fixed_operators/rtl/fixed_dot_product.sv",
                "linear_layers/fixed_operators/rtl/fixed_vector_mult.sv",
                "linear_layers/fixed_operators/rtl/fixed_accumulator.sv",
                "linear_layers/fixed_operators/rtl/fixed_adder_tree.sv",
                "linear_layers/fixed_operators/rtl/fixed_adder_tree_layer.sv",
                "linear_layers/fixed_operators/rtl/fixed_mult.sv",
                "common/rtl/register_slice.sv",
                "common/rtl/join2.sv",
                "memory/rtl/unpacked_repeat_circular_buffer.sv",
                "memory/rtl/skid_buffer.sv",
                "linear_layers/fixed_linear_layer/rtl/fixed_linear.sv",
                "linear_layers/matmul/rtl/matrix_flatten.sv",
                "linear_layers/matmul/rtl/matrix_unflatten.sv",
                "linear_layers/matmul/rtl/matrix_fifo.sv",
                "linear_layers/matmul/rtl/matrix_accumulator.sv",
                "linear_layers/matmul/rtl/simple_matmul.sv",
                "linear_layers/matmul/rtl/matmul.sv",
                "linear_layers/matmul/rtl/transpose.sv",
                "linear_layers/matmul/rtl/matrix_stream_transpose.sv",
            ],
        },
    ],
    "relu": [
        {
            "name": "fixed_relu",
            "dependence_files": [
                "activation_layers/rtl/fixed_relu.sv",
            ],
        },
    ],
    "hardshrink": [
        {
            "name": "fixed_hardshrink",
            "dependence_files": [
                "activation_layers/rtl/fixed_hardshrink.sv",
            ],
        },
    ],
    "silu": [
        {
            "name": "fixed_silu",
            "dependence_files": [
                "activation_layers/rtl/fixed_silu.sv",
                "activation_layers/rtl/silu_lut.sv",
            ],
        },
    ],
    "elu": [
        {
            "name": "fixed_elu",
            "dependence_files": [
                "activation_layers/rtl/fixed_elu.sv",
                "activation_layers/rtl/elu_lut.sv",
            ],
        },
    ],
    "sigmoid": [
        {
            "name": "fixed_sigmoid",
            "dependence_files": [
                "activation_layers/rtl/fixed_sigmoid.sv",
                "activation_layers/rtl/sigmoid_lut.sv",
            ],
        },
    ],
    "softshrink": [
        {
            "name": "fixed_softshrink",
            "dependence_files": [
                "activation_layers/rtl/fixed_softshrink.sv",
            ],
        },
    ],
    "logsigmoid": [
        {
            "name": "fixed_logsigmoid",
            "dependence_files": [
                "activation_layers/rtl/fixed_logsigmoid.sv",
                "activation_layers/rtl/logsigmoid_lut.sv",
            ],
        },
    ],
    "softmax": [
        {
            "name": "fixed_softmax",
            "dependence_files": [
                "activation_layers/rtl/fixed_softmax.sv",
                "activation_layers/rtl/exp_lut .sv",
            ],
        }
    ],
    "batch_norm2d": [norm],
    "layer_norm": [norm],
    "group_norm": [norm],
    "instance_norm2d": [norm],
    "rms_norm": [norm],
    "selu": [
        {
            "name": "fixed_selu",
            "dependence_files": [
                "activation_layers/rtl/fixed_selu.sv",
            ],
        },
    ],
    "tanh": [
        {
            "name": "fixed_tanh",
            "dependence_files": [
                "activation_layers/rtl/fixed_tanh.sv",
            ],
        },
    ],
    "gelu": [
        {
            "name": "fixed_gelu",
            "dependence_files": [
                "activation_layers/rtl/fixed_gelu.sv",
                "activation_layers/rtl/gelu_lut.sv",
            ],
        },
    ],
    "softsign": [
        {
            "name": "fixed_softsign",
            "dependence_files": [
                "activation_layers/rtl/fixed_softsign.sv",
                "linear_layers/fixed_operators/rtl/fixed_mult.sv",
            ],
        },
    ],
    "softplus": [
        {
            "name": "fixed_softplus",
            "dependence_files": [
                "activation_layers/rtl/fixed_softplus.sv",
            ],
        },
    ],
    "add": [
        {
            "name": "fixed_adder",
            "dependence_files": [
                "linear_layers/fixed_operators/rtl/fixed_adder.sv",
            ],
        }
    ],
    "mul": [
        {
            "name": "fixed_elementwise_multiplier",
            "dependence_files": [
                "linear_layers/fixed_operators/rtl/fixed_vector_mult.sv",
            ],
        }
    ],
    "df_split": [
        {
            "name": "df_split",
            "dependence_files": ["common/rtl/df_split.sv", "common/rtl/split2.sv"],
        }
    ],
    "getitem": [
        {
            "name": "buffer",
            "dependence_files": [
                "memory/rtl/buffer.sv",
            ],
        }
    ],
    "grouped_query_attention": [
        {
            "name": "fixed_gqa_wrapper",
            "dependence_files": [
                "common/rtl/find_first_arbiter.sv",
                "common/rtl/mux.sv",
                "common/rtl/join2.sv",
                "common/rtl/split2.sv",
                "common/rtl/split_n.sv",
                "common/rtl/join_n.sv",
                "memory/rtl/repeat_circular_buffer.sv",
                "common/rtl/single_element_repeat.sv",
                "memory/rtl/skid_buffer.sv",
                "memory/rtl/unpacked_skid_buffer.sv",
                "common/rtl/register_slice.sv",
                "memory/rtl/simple_dual_port_ram.sv",
                "memory/rtl/fifo.sv",
                "common/rtl/lut.sv",
                "common/rtl/comparator_tree.sv",
                "common/rtl/comparator_accumulator.sv",
                "common/rtl/unpacked_register_slice.sv",
                "cast/rtl/fixed_round.sv",
                "cast/rtl/fixed_rounding.sv",
                "cast/rtl/floor_round.sv",
                "cast/rtl/signed_clamp.sv",
                "cast/rtl/fixed_signed_cast.sv",
                "linear_layers/fixed_operators/rtl/fixed_mult.sv",
                "linear_layers/fixed_operators/rtl/fixed_vector_mult.sv",
                "linear_layers/fixed_operators/rtl/fixed_dot_product.sv",
                "linear_layers/fixed_operators/rtl/fixed_accumulator.sv",
                "linear_layers/fixed_operators/rtl/fixed_adder_tree_layer.sv",
                "linear_layers/fixed_operators/rtl/fixed_adder_tree.sv",
                "linear_layers/fixed_operators/rtl/fixed_range_reduction.sv",
                "linear_layers/fixed_linear_layer/rtl/fixed_linear.sv",
                "linear_layers/matmul/rtl/matrix_flatten.sv",
                "linear_layers/matmul/rtl/matrix_unflatten.sv",
                "linear_layers/matmul/rtl/matrix_fifo.sv",
                "linear_layers/matmul/rtl/matrix_accumulator.sv",
                "linear_layers/matmul/rtl/simple_matmul.sv",
                "linear_layers/matmul/rtl/matmul.sv",
                "linear_layers/matmul/rtl/transpose.sv",
                "linear_layers/matmul/rtl/matrix_stream_transpose.sv",
                "activation_layers/rtl/softermax_lpw_pow2.sv",
                "activation_layers/rtl/softermax_lpw_reciprocal.sv",
                "activation_layers/rtl/softermax_local_window.sv",
                "activation_layers/rtl/softermax_global_norm.sv",
                "activation_layers/rtl/fixed_softermax_1d.sv",
                "activation_layers/rtl/fixed_softermax.sv",
                "transformer_layers/rtl/fixed_gqa_projections.sv",
                "transformer_layers/rtl/self_attention_head_single_scatter.sv",
                "transformer_layers/rtl/gqa_head_scatter_control.sv",
                "transformer_layers/rtl/self_attention_head_gather.sv",
                "transformer_layers/rtl/fixed_self_attention_head.sv",
                "transformer_layers/rtl/fixed_grouped_query_attention.sv",
                "transformer_layers/rtl/fixed_gqa_wrapper.sv",
            ],
        }
    ],
}
