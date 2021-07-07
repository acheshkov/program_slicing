from _ast import AST
from pathlib import Path

from extract_method_dataset.inline_dataset.utils import method_body_lines
from veniq.ast_framework import AST, ASTNodeType, ASTNode
from veniq.dataset_collection.types_identifier import AlgorithmFactory, InlineTypesAlgorithms
from veniq.utils.ast_builder import build_ast
from veniq.utils.encoding_detector import read_text_with_autodetected_encoding

from program_slicing.decomposition.block_slicing import get_block_slices
from program_slicing.decomposition.slicing import get_complete_computation_slices
from program_slicing.graph.parse import LANG_JAVA
import operator
from functools import reduce
import pandas as pd

text = '''

		String attribute = getApplicationAttribute();

		// first see if the application name has been set on the launch config
		String application = config.getAttribute(attribute, (String) null);
		if (application == null || fApplicationCombo.indexOf(application) == -1) {
			application = null;

			// check if the user has entered the -application arg in the program arg field
			StringTokenizer tokenizer = new StringTokenizer(config.getAttribute(IJavaLaunchConfigurationConstants.ATTR_PROGRAM_ARGUMENTS, "")); //$NON-NLS-1$
			while (tokenizer.hasMoreTokens()) {
				String token = tokenizer.nextToken();
				if (token.equals("-application") && tokenizer.hasMoreTokens()) { //$NON-NLS-1$
					application = tokenizer.nextToken();
					break;
				}
			}

			int index = -1;
			if (application != null)
				index = fApplicationCombo.indexOf(application);

			// use default application as specified in the install.ini of the target platform
			if (index == -1)
				index = fApplicationCombo.indexOf(TargetPlatform.getDefaultApplication());

			if (index != -1) {
				fApplicationCombo.setText(fApplicationCombo.getItem(index));
			} else if (fApplicationCombo.getItemCount() > 0) {
				fApplicationCombo.setText(fApplicationCombo.getItem(0));
			}
		} else {
			fApplicationCombo.setText(application);
		}
'''

lst = get_block_slices(text, LANG_JAVA, max_percentage=1.00)
print(lst)