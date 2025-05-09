from .quantization import (
    ManualHFModuleSearchSpaceMixedPrecisionPTQ,
    GraphSearchSpaceMixedPrecisionPTQ,
)
from .systolic import SystolicMappingSearchSpace
from .base import SearchSpaceBase

from chop.tools.check_dependency import check_deps_tensorRT_pass

# from .nas_bert import NasBertSpace

SEARCH_SPACE_MAP = {
    "graph/quantize/mixed_precision_ptq": GraphSearchSpaceMixedPrecisionPTQ,
    "module/manual_hf/quantize/llm_mixed_precision_ptq": ManualHFModuleSearchSpaceMixedPrecisionPTQ,
    "graph/hardware/systolic_mapping": SystolicMappingSearchSpace,
}

if check_deps_tensorRT_pass(silent=True):
    from .trt import GraphSearchSpaceTRTMixedPrecisionPTQ

    # enable the search space for tensorrt if it is correctly installed
    SEARCH_SPACE_MAP["graph/tensorrt/mixed_precision_ptq"] = (
        GraphSearchSpaceTRTMixedPrecisionPTQ,
    )


def get_search_space_cls(name: str) -> SearchSpaceBase:
    """
    Get the search space class by name.

    Args:
        name: the name of the search space class

    Returns:
        the search space class

    ---

    Available search space classes:
    - "graph/quantize/mixed_precision_ptq" -> `GraphSearchSpaceMixedPrecisionPTQ`:
    the search space for mixed-precision post-training-quantization quantization search on mase graph
    - "module/manual_hf/quantize/llm_mixed_precision_ptq" -> `ManualHFModuleSearchSpaceMixedPrecisionPTQ`:
    the search space for mixed-precision post-training-quantization quantization search on HuggingFace's PreTrainedModel
    """
    if name not in SEARCH_SPACE_MAP:
        raise ValueError(f"{name} must be defined in {list(SEARCH_SPACE_MAP.keys())}.")
    return SEARCH_SPACE_MAP[name]
