''' LARK-AG: A Python library for providing Attribute Grammar support to Lark. '''

#Read version from pyproject.toml
from importlib.metadata import version
__version__ = "1.0.3"

from .generator_layer import GeneratorLayer
from .processor_layer import ProcessorLayer

from .errors import AGDefinitionError, CircularDependencyError, ContextConditionError
from .lark_ag import Lark_AG

__all__ = ('GeneratorLayer', 'ProcessorLayer', 'Lark_AG',
           'AGDefinitionError', 'CircularDependencyError', 'ContextConditionError')