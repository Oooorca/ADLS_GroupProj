from functools import partial

from chop.nn.quantized.functional.linear import (
    linearBinary,
    linearBinaryScaling,
    linearBlockFP,
    linearBlockLog,
    linearBlockMinifloat,
    linearInteger,
    linearLog,
    linearMXIntHardware,
    linearMinifloatDenorm,
    linearMinifloatIEEE,
    linearTernary,
)
import torch
from torch import Tensor
from torch.nn import functional as F


from ..utils import get_stats, quantiser_passthrough

from chop.nn.quantizers import (
    residual_sign_quantizer,
    block_fp_quantizer,
    block_log_quantizer,
    block_minifloat_quantizer,
    integer_quantizer,
    integer_floor_quantizer,
    log_quantizer,
    minifloat_denorm_quantizer,
    minifloat_ieee_quantizer,
    binary_quantizer,
    ternary_quantizer,
    mxint_hardware,
)

# LUTNet
import numpy as np
from typing import Type
from chop.nn.quantizers.LUTNet.BaseTrainer import BaseTrainer, LagrangeTrainer
from chop.nn.quantizers.LUTNet.MaskBase import MaskBase, MaskExpanded

# LogicNets
from chop.nn.quantizers.LogicNets.utils import (
    generate_permutation_matrix,
    get_int_state_space,
    fetch_mask_indices,
)

# LogicNets
from chop.nn.quantizers.LogicNets.utils import (
    generate_permutation_matrix,
    get_int_state_space,
    fetch_mask_indices,
)


class _LinearBase(torch.nn.Linear):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        bias: bool = False,
        device=None,
        dtype=None,
    ) -> None:
        super().__init__(
            in_features,
            out_features,
            bias,
            device,
            dtype,
        )
        self.bypass = False
        self.pruning_masks = None
        # NOTE: Quantizers properties are not needed for now
        # self.x_quantizer = None
        # self.w_quantizer = None
        # self.b_quantizer = None
        # self.out_quantizer = None

    # NOTE: This is not needed for now
    # def forward(self, x: Tensor) -> Tensor:
    #     if self.bypass:
    #         # if bypass, there is no quantization
    #         return F.linear(x, self.weight, self.bias)
    #     else:
    #         x = self.x_quantizer(x)
    #         w = self.w_quantizer(self.weight)
    #         bias = self.b_quantizer(self.bias) if self.bias is not None else None
    #         out = F.linear(x, w, bias)
    #         if self.out_quantizer is None:
    #             return out
    #         return self.out_quantizer(out)


class LinearInteger(_LinearBase):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        bias: bool = True,
        device=None,
        dtype=None,
        config=None,
        out_config=None,
        floor=None,
    ) -> None:
        super().__init__(in_features, out_features, bias, device, dtype)
        assert config is not None, "config is None!"
        # Add floor attribute to the config
        if floor is not None:
            config["floor"] = floor
        self.config = config
        self.out_config = out_config
        self.bypass = config.get("bypass", False)
        if self.bypass:
            return

    def forward(self, x):
        if self.bypass:
            return F.linear(x, self.weight, self.bias)
        return linearInteger(x, self.weight, self.bias, self.config, self.out_config)


class LinearMinifloatDenorm(_LinearBase):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        bias: bool = True,
        device=None,
        dtype=None,
        config=None,
    ) -> None:
        super().__init__(in_features, out_features, bias, device, dtype)
        assert config is not None, "config is None!"
        self.config = config
        self.bypass = config.get("bypass", False)
        if self.bypass:
            return

    def forward(self, x):
        if self.bypass:
            return F.linear(x, self.weight, self.bias)
        return linearMinifloatDenorm(x, self.weight, self.bias, self.config)


class LinearMinifloatIEEE(_LinearBase):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        bias: bool = True,
        device=None,
        dtype=None,
        config=None,
    ) -> None:
        super().__init__(in_features, out_features, bias, device, dtype)

        assert config is not None, "config is None!"
        self.config = config
        self.bypass = config.get("bypass", False)
        if self.bypass:
            return

    def forward(self, x):
        if self.bypass:
            return F.linear(x, self.weight, self.bias)
        return linearMinifloatIEEE(x, self.weight, self.bias, self.config)


class LinearLog(_LinearBase):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        bias: bool = True,
        device=None,
        dtype=None,
        config=None,
    ) -> None:
        super().__init__(in_features, out_features, bias, device, dtype)
        assert config is not None, "config is None!"
        self.config = config
        self.bypass = config.get("bypass", False)
        if self.bypass:
            return

    def forward(self, x):
        if self.bypass:
            return F.linear(x, self.weight, self.bias)
        return linearLog(x, self.weight, self.bias, self.config)


class LinearBlockFP(_LinearBase):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        bias: bool = True,
        device=None,
        dtype=None,
        config=None,
    ) -> None:
        super().__init__(in_features, out_features, bias, device, dtype)
        assert config is not None, "config is None!"
        self.config = config
        self.bypass = config.get("bypass", False)
        if self.bypass:
            return

    def forward(self, x):
        if self.bypass:
            return F.linear(x, self.weight, self.bias)
        return linearBlockFP(x, self.weight, self.bias, self.config)


class LinearBlockMinifloat(_LinearBase):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        bias: bool = True,
        device=None,
        dtype=None,
        config=None,
    ) -> None:
        super().__init__(in_features, out_features, bias, device, dtype)

        assert config is not None, "config is None!"
        self.config = config
        self.bypass = config.get("bypass", False)
        if self.bypass:
            return

    def forward(self, x):
        if self.bypass:
            return F.linear(x, self.weight, self.bias)
        return linearBlockMinifloat(x, self.weight, self.bias, self.config)


class LinearBlockLog(_LinearBase):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        bias: bool = True,
        device=None,
        dtype=None,
        config=None,
    ) -> None:
        super().__init__(in_features, out_features, bias, device, dtype)

        assert config is not None, "config is None!"
        self.config = config
        self.bypass = config.get("bypass", False)
        if self.bypass:
            return

    def forward(self, x):
        if self.bypass:
            return F.linear(x, self.weight, self.bias)
        return linearBlockLog(x, self.weight, self.bias, self.config)


class LinearBinary(_LinearBase):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        bias: bool = True,
        device=None,
        dtype=None,
        config=None,
    ) -> None:
        super().__init__(in_features, out_features, bias, device, dtype)
        assert config is not None, "config is None!"
        self.config = config
        self.bypass = config.get("bypass", False)
        if self.bypass:
            return

    def forward(self, x):
        if self.bypass:
            return F.linear(x, self.weight, self.bias)
        return linearBinary(x, self.weight, self.bias, self.config)


class LinearBinaryScaling(_LinearBase):
    """
    Binary scaling variant of the linear transformation layer.

        - "bypass": Bypass quantization for standard linear transformation.
        - "data_in_stochastic", "bias_stochastic", "weight_stochastic": Stochastic settings.
        - "data_in_bipolar", "bias_bipolar", "weight_bipolar": Bipolar settings.
        - "binary_training": Apply binary scaling during training.
    """

    def __init__(
        self,
        in_features: int,
        out_features: int,
        bias: bool = True,
        device=None,
        dtype=None,
        config=None,
    ) -> None:
        super().__init__(in_features, out_features, bias, device, dtype)
        assert config is not None, "config is None!"
        self.config = config
        self.bypass = config.get("bypass", False)
        # self.gamma = torch.nn.Parameter(torch.tensor(1.0, requires_grad=True))
        if self.bypass:
            return

    def forward(self, x):
        if self.bypass:
            return F.linear(x, self.weight, self.bias)
        return linearBinaryScaling(x, self.weight, self.bias, self.config)


class LinearTernary(_LinearBase):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        bias: bool = True,
        device=None,
        dtype=None,
        config=None,
    ) -> None:
        super().__init__(in_features, out_features, bias, device, dtype)
        assert config is not None, "config is None!"
        self.config = config
        self.bypass = config.get("bypass", False)
        if self.bypass:
            return

        w_scaling_factor = config["weight_scaling_factor"]
        w_mean = get_stats(config, "weight_mean")
        w_median = get_stats(config, "weight_median")
        w_max = get_stats(config, "weight_max")
        self.w_quantizer = partial(
            ternary_quantizer,
            scaling_factor=w_scaling_factor,
            maximum=w_max,
            median=w_median,
            mean=w_mean,
        )
        self.x_quantizer = quantiser_passthrough
        self.b_quantizer = quantiser_passthrough
        # self.b_quantizer = partial(
        #     ternary_quantizer,
        #     scaling_factor=b_scaling_factor,
        #     maximum=b_max,
        #     median=b_median,
        #     mean=b_mean,
        # )

    def forward(self, x):
        if self.bypass:
            return F.linear(x, self.weight, self.bias)
        return linearTernary(x, self.weight, self.bias, self.config)


# LUT
class LinearBinaryResidualSign(_LinearBase):
    """
    Binary Linear layer with redisual sign variant of the linear transformation layer.

        - "bypass": Bypass quantization for standard linear transformation.
        - "data_in_stochastic", "bias_stochastic", "weight_stochastic": Stochastic settings.
        - "data_in_bipolar", "bias_bipolar", "weight_bipolar": Bipolar settings.
        - "binary_training": Apply binary scaling during training.
        - "data_in_levels": The num of residual layers to use.
        - "data_in_residual_sign" : Apply residual sign on input
    """

    def __init__(
        self,
        in_features: int,
        out_features: int,
        bias: bool = True,
        device=None,
        dtype=None,
        config=None,
    ) -> None:
        super().__init__(in_features, out_features, bias, device, dtype)
        assert config is not None, "config is None!"
        self.levels = config.get("data_in_levels", 2)  # NOTE: Hardcode 2 for now
        self.config = config
        self.bypass = config.get("bypass", False)
        self.gamma = torch.nn.Parameter(torch.tensor(1.0, requires_grad=True))
        # Initialized parameter
        ars = np.arange(self.levels) + 1.0
        ars = ars[::-1]
        means = ars / np.sum(ars)
        # Create a torch.nn.Parameter from the means tensor
        self.means = (
            torch.nn.Parameter(
                torch.tensor(means, dtype=torch.float32, requires_grad=True)
            )
            if self.config.get("data_in_residual_sign", True)
            else None
        )
        # prunning masks
        self.pruning_masks = torch.nn.Parameter(
            torch.ones_like(self.weight), requires_grad=False
        )

        if self.bypass:
            return
        x_stochastic, w_stochastic = (
            config["data_in_stochastic"],
            config["weight_stochastic"],
        )
        x_bipolar, w_bipolar = (
            config["data_in_bipolar"],
            config["weight_bipolar"],
        )

        self.binary_training = config["binary_training"]

        self.w_quantizer = partial(
            binary_quantizer, stochastic=w_stochastic, bipolar=w_bipolar
        )
        self.x_quantizer = partial(
            binary_quantizer, stochastic=x_stochastic, bipolar=x_bipolar
        )

    def forward(self, x: Tensor) -> Tensor:
        if self.bypass:
            # if bypss, there is no quantization
            return F.linear(x, self.weight, self.bias)

        x_expanded = 0
        if self.means is not None:
            out_bin = residual_sign_quantizer(
                levels=self.levels, x_quantizer=self.x_quantizer, means=self.means, x=x
            )
            for l in range(self.levels):
                x_expanded = x_expanded + out_bin[l, :, :]
        else:
            x_expanded = x

        if self.binary_training:
            w = self.w_quantizer(self.weight)
            return F.linear(
                x_expanded,
                w * self.gamma.abs() * self.pruning_masks,
                self.bias,
            )
        else:
            self.weigh = self.weight.data.clamp_(-1, 1)
            return F.linear(
                x_expanded,
                self.weight * self.gamma.abs() * self.pruning_masks,
                self.bias,
            )


class LinearLUT(torch.nn.Module):
    input_mask: torch.Tensor
    tables_count: int
    in_features: int
    out_features: int
    trainer: BaseTrainer
    mask_builder_type: Type[MaskBase]
    mask_builder: MaskBase

    def __init__(
        self,
        config: None,
        in_features: int,
        out_features: int,
        mask_builder_type: Type[MaskBase] = MaskExpanded,
        trainer_type: Type[BaseTrainer] = LagrangeTrainer,
        bias: bool = True,
        device: str = None,
    ) -> None:
        super(LinearLUT, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.levels = config.get("data_in_levels", 2)
        self.input_expanded = config["data_in_input_expanded"]
        self.k = config["data_in_k"]
        self.kk = 2 ** config["data_in_k"]
        self.mask_builder_type = mask_builder_type
        # Initialize mask builder
        self.input_mask = self._input_mask_builder()
        # TODO: table * output feature map
        self.tables_count = self.mask_builder.get_tables_count() * self.out_features
        self.trainer = trainer_type(
            levels=self.levels,
            tables_count=self.tables_count,
            k=config["data_in_k"],
            binarization_level=(1 if config["data_in_binarization_level"] == 1 else 0),
            input_expanded=config["data_in_input_expanded"],
            device=device,
        )
        self.weight = self.trainer.weight
        self.pruning_masks = self.trainer.pruning_masks
        # TODO: we might need to this later on
        # stdv = 1 / np.sqrt(self.in_features)
        # w = np.random.normal(loc=0.0, scale=stdv, size=list(self.trainer.weight.shape)).astype(np.float32)
        # self.trainer.weight = torch.nn.Parameter(
        #    torch.tensor(w, requires_grad=True))

        self.bias = (
            torch.nn.Linear(1, out_features, device=device).bias if bias else None
        )

        # Residual sign code
        self.x_quantizer = partial(binary_quantizer, stochastic=False, bipolar=True)
        ars = np.arange(self.levels) + 1.0
        ars = ars[::-1]
        means = ars / np.sum(ars)
        self.means = torch.nn.Parameter(
            torch.tensor(means, dtype=torch.float32, requires_grad=True)
        )

    def _table_input_selections_builder(self) -> np.array:
        _all_inputs_set = set(range(self.in_features))
        result = []
        for in_idx in range(self.in_features):
            _idx_set = set([in_idx])
            _selection = list(_all_inputs_set - _idx_set)
            result.append((in_idx, _selection))
        return result

    def _input_mask_builder(self) -> torch.Tensor:
        """
        Initializing table (using indices for the connections)
        """
        result = []
        # TODO: elements can appear more than once in the feature-1 input?
        for _ in range(self.out_features):
            self.mask_builder = self.mask_builder_type(
                self.k, self._table_input_selections_builder(), True
            )
            result.append(self.mask_builder.build())
        return np.concatenate(result)

    def forward(
        self,
        input: torch.Tensor,
        targets: torch.tensor = None,
        initalize: bool = False,
    ):
        assert len(input.shape) == 2
        batch_size = input.shape[0]
        out_bin = residual_sign_quantizer(
            levels=self.levels, x_quantizer=self.x_quantizer, means=self.means, x=input
        )
        expanded_input = out_bin[:, :, self.input_mask]  # [levels, batch_size, mask]

        output = self.trainer(expanded_input, targets, initalize).squeeze()
        output = output.view(batch_size, -1)
        assert output.shape[-1] == self.tables_count
        output = output.view(
            batch_size,
            self.out_features,
            int(self.tables_count / self.out_features),
        )
        output = output.sum(-1)
        if self.bias is not None:
            output = output + self.bias
        return output

    def pre_initialize(self):
        self.trainer.clear_initializion()

    def update_initialized_weights(self):
        self.trainer.update_initialized_weights()


class LinearLogicNets(_LinearBase):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        bias: bool = True,
        device=None,
        dtype=None,
        config=None,
        activation_module=None,  # To initialize a LogicNets, activation functions are needed
        input_layers=None,  # A LogicNets layer may be merged with one or more inputs layers such as activations and batchnorm
        output_layers=None,  # A LogicNets layer may be merged with one or more output layers such as activations and batchnorm
    ) -> None:
        super().__init__(in_features, out_features, bias, device, dtype)
        assert config is not None, "config is None!"
        self.config = config
        self.bypass = config.get("bypass", False)
        if self.bypass:
            return
        # establish quantizer
        self.x_width, self.x_frac_width = (
            config["data_in_width"],
            config["data_in_frac_width"],
        )
        self.y_width, self.y_frac_width = (
            config["data_out_width"],
            config["data_out_frac_width"],
        )

        self.x_quantizer = partial(
            integer_quantizer, width=self.x_width, frac_width=self.x_frac_width
        )
        self.y_quantizer = partial(
            integer_quantizer, width=self.y_width, frac_width=self.y_frac_width
        )

        # self.input_quant = input_quant
        # self.output_quant = output_quant
        self.activation = activation_module
        self.is_lut_inference = True
        self.neuron_truth_tables = None
        # self.calculate_truth_tables()
        # self.apply_input_quant = apply_input_quant
        # self.apply_output_quant = apply_output_quant
        self.input_layers = input_layers
        self.output_layers = output_layers
        self.apply_layers = False

    # TODO: This function might be a useful utility outside of this class..
    def table_lookup(
        self,
        connected_input: Tensor,
        input_perm_matrix: Tensor,
        bin_output_states: Tensor,
    ) -> Tensor:
        fan_in_size = connected_input.shape[1]
        ci_bcast = connected_input.unsqueeze(2)  # Reshape to B x Fan-in x 1
        pm_bcast = input_perm_matrix.t().unsqueeze(
            0
        )  # Reshape to 1 x Fan-in x InputStates
        eq = (ci_bcast == pm_bcast).sum(
            dim=1
        ) == fan_in_size  # Create a boolean matrix which matches input vectors to possible input states
        matches = eq.sum(dim=1)  # Count the number of perfect matches per input vector
        if not (matches == torch.ones_like(matches, dtype=matches.dtype)).all():
            raise Exception(
                f"One or more vectors in the input is not in the possible input state space"
            )
        indices = torch.argmax(eq.type(torch.int64), dim=1)
        return bin_output_states[indices]

    def lut_forward(self, x: Tensor) -> Tensor:
        x = torch.flatten(
            x, 1
        )  # N - added this; is 1 needed to flatten all dims except batch?
        # if self.apply_input_quant:
        #     x = self.input_quant(x) # Use this to fetch the bin output of the input, if the input isn't already in binary format
        x = self.encode(self.x_quantizer(x))
        y = torch.zeros((x.shape[0], self.out_features))
        # Perform table lookup for each neuron output
        for i in range(self.out_features):
            indices, input_perm_matrix, bin_output_states = self.neuron_truth_tables[i]
            # Move logicnets tensor to GPU
            input_perm_matrix = input_perm_matrix.to(x.device)
            bin_output_states = bin_output_states.to(x.device)
            connected_input = x[:, indices]
            y[:, i] = self.table_lookup(
                connected_input, input_perm_matrix, bin_output_states
            )
        return y

    def construct_mask_index(self):
        # contract a mask have the same shape as self.weight but with zero element being assign to zero and other assign to 1
        self.mask = torch.where(
            self.weight != 0, torch.tensor(1), torch.tensor(0)
        ).reshape(
            self.weight.shape[0], -1
        )  # pay attention to dimension (out_feature, in_feature)

    # Consider using masked_select instead of fetching the indices
    def calculate_truth_tables(self):
        # print(
        #     "weight", torch.where(self.weight != 0, torch.tensor(1), torch.tensor(0))
        # )  # pay attention to dimension (out_feature, in_feature)
        with torch.no_grad():
            # Precalculate all of the input value permutations
            input_state_space = list()  # TODO: is a list the right data-structure here?
            bin_state_space = list()
            # get a neuron_state
            for m in range(self.in_features):
                neuron_state_space = self.decode(
                    get_int_state_space(self.x_width)
                )  # TODO: this call should include the index of the element of interest
                bin_space = get_int_state_space(
                    self.x_width
                )  # TODO: this call should include the index of the element of interest
                input_state_space.append(neuron_state_space)
                bin_state_space.append(bin_space)

            neuron_truth_tables = list()
            self.construct_mask_index()  # construct pruning mask
            for n in range(self.out_features):
                input_mask = self.mask[
                    n, :
                ]  # N: select row of mask tensor that corresponds to the output feature on this iteration
                fan_in = torch.sum(input_mask)
                indices = fetch_mask_indices(input_mask)
                # Generate a matrix containing all possible input states
                input_permutation_matrix = generate_permutation_matrix(
                    [input_state_space[i] for i in indices]
                )
                bin_input_permutation_matrix = generate_permutation_matrix(
                    [bin_state_space[i] for i in indices]
                )
                # TODO: Update this block to just run inference on the fc layer, once BN has been moved to output_quant
                num_permutations = input_permutation_matrix.shape[0]
                padded_perm_matrix = torch.zeros((num_permutations, self.in_features))
                padded_perm_matrix[:, indices] = input_permutation_matrix

                bin_output_states = self.encode(self.math_forward(padded_perm_matrix))[
                    :, n
                ]  # Calculate bin for the current input

                # Append the connectivity, input permutations and output permutations to the neuron truth tables
                neuron_truth_tables.append(
                    (indices, bin_input_permutation_matrix, bin_output_states)
                )  # Change this to be the binary output states
        self.neuron_truth_tables = neuron_truth_tables

    def math_forward(self, input: Tensor) -> Tensor:
        if self.activation == "unittest":
            # This is the for performing unittest on the layer
            return self.y_quantizer(
                F.linear(self.x_quantizer(input), self.weight, self.bias)
            )

        if self.apply_layers:
            x = input
            if self.input_layers:
                x = self.run_layers(x, self.input_layers)

            y = self.y_quantizer(F.linear(self.x_quantizer(x), self.weight, self.bias))

            if self.output_layers:
                y = self.run_layers(y, self.output_layers)
            return y

        # This is the case where the linear layer is the only module in the LogicNets module
        return self.y_quantizer(
            F.linear(self.x_quantizer(input), self.weight, self.bias)
        )

    def set_fused(self, fused: bool):
        self.apply_layers = fused

    def run_layers(self, input: Tensor, layers) -> Tensor:
        assert isinstance(layers, list)
        y = input
        for layer in layers:
            layer_name = layer.__class__.__name__
            SUPPORTED_LAYERS = {
                "ReLU": 1,
                "Tanh": 1,
                "BatchNorm1d": 1,
                "str": 0,
            }  # "str" type is short the "output". Hence this logicnets will be a pure linear without activation.
            if layer_name not in SUPPORTED_LAYERS:
                raise ValueError(
                    "Unsupported output layer {}. Please choose from {}".format(
                        layer_name, list(SUPPORTED_LAYERS.keys())
                    )
                )
            if SUPPORTED_LAYERS[layer_name]:
                y = layer(y)
        return y

    def encode(self, input: Tensor) -> Tensor:
        return input * 2**self.x_frac_width

    def decode(self, input: Tensor) -> Tensor:
        return input / 2**self.x_frac_width

    def forward(self, x: Tensor) -> Tensor:
        if self.is_lut_inference:
            return self.decode(self.lut_forward(x))
        else:
            return self.math_forward(x)


class LinearMXIntHardware(_LinearBase):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        bias: bool = True,
        device=None,
        dtype=None,
        config=None,
        out_config=None,
    ) -> None:
        super().__init__(in_features, out_features, bias, device, dtype)
        assert config is not None, "config is None!"
        self.config = config
        self.out_config = out_config
        self.bypass = config.get("bypass", False)
        if self.bypass:
            return

    def forward(self, x):
        if self.bypass:
            return F.linear(x, self.weight, self.bias)
        return linearMXIntHardware(
            x, self.weight, self.bias, self.config, self.out_config
        )
