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

text = '''
if (importRewrite == null) {
			return null;
		}
		ICompilationUnit workingCopy = null;
		try {
			String name = "Type" + System.currentTimeMillis(); //$NON-NLS-1$
			workingCopy = fCompilationUnit.getPrimary().getWorkingCopy(null);
			ISourceRange range = fSuperType.getSourceRange();
			boolean sameUnit = range != null && fCompilationUnit.equals(fSuperType.getCompilationUnit());
			String dummyClassContent = createDummyType(name);
			StringBuffer workingCopyContents = new StringBuffer(fCompilationUnit.getSource());
			int insertPosition;
			if (sameUnit) {
				insertPosition = range.getOffset() + range.getLength();
			} else {
				ISourceRange firstTypeRange = fCompilationUnit.getTypes()[0].getSourceRange();
				insertPosition = firstTypeRange.getOffset();
			}
			if (fSuperType.isLocal()) {
				workingCopyContents.insert(insertPosition, '{' + dummyClassContent + '}');
				insertPosition++;
			} else {
				workingCopyContents.insert(insertPosition, dummyClassContent + "\n\n"); //$NON-NLS-1$
			}
			workingCopy.getBuffer().setContents(workingCopyContents.toString());
			ASTParser parser = ASTParser.newParser(IASTSharedValues.SHARED_AST_LEVEL);
			parser.setResolveBindings(true);
			parser.setStatementsRecovery(true);
			parser.setSource(workingCopy);
			CompilationUnit astRoot = (CompilationUnit) parser.createAST(new NullProgressMonitor());
			ASTNode newType = NodeFinder.perform(astRoot, insertPosition, dummyClassContent.length());
			if (!(newType instanceof AbstractTypeDeclaration)) {
				return null;
			}
			AbstractTypeDeclaration declaration = (AbstractTypeDeclaration) newType;
			ITypeBinding dummyTypeBinding = declaration.resolveBinding();
			if (dummyTypeBinding == null) {
				return null;
			}
			IMethodBinding[] bindings = StubUtility2Core.getOverridableMethods(astRoot.getAST(), dummyTypeBinding, true);
			if (fSuperType.isInterface()) {
				ITypeBinding[] dummySuperInterfaces = dummyTypeBinding.getInterfaces();
				if (dummySuperInterfaces.length == 0 || dummySuperInterfaces.length == 1 && dummySuperInterfaces[0].isRawType()) {
					bindings = new IMethodBinding[0];
				}
			} else {
				ITypeBinding dummySuperclass = dummyTypeBinding.getSuperclass();
				if (dummySuperclass == null || dummySuperclass.isRawType()) {
					bindings = new IMethodBinding[0];
				}
			}
			CodeGenerationSettings settings = PreferenceManager.getCodeGenerationSettings(fJavaProject.getProject());
			IMethodBinding[] methodsToOverride = null;
			settings.createComments = false;
			List<IMethodBinding> result = new ArrayList<>();
			for (int i = 0; i < bindings.length; i++) {
				IMethodBinding curr = bindings[i];
				if (Modifier.isAbstract(curr.getModifiers())) {
					result.add(curr);
				}
			}
			methodsToOverride = result.toArray(new IMethodBinding[result.size()]);
			ASTNode focusNode = null;
			IBinding contextBinding = null; // used to find @NonNullByDefault effective at that current context
			if (fCompilationUnit.getJavaProject().getOption(JavaCore.COMPILER_ANNOTATION_NULL_ANALYSIS, true).equals(JavaCore.ENABLED)) {
				focusNode = NodeFinder.perform(astRoot, fReplacementOffset + dummyClassContent.length(), 0);
				contextBinding = getEnclosingDeclaration(focusNode);
			}
			ASTRewrite rewrite = ASTRewrite.create(astRoot.getAST());
			ITrackedNodePosition trackedDeclaration = rewrite.track(declaration);
			ListRewrite rewriter = rewrite.getListRewrite(declaration, declaration.getBodyDeclarationsProperty());
			for (int i = 0; i < methodsToOverride.length; i++) {
				boolean snippetSupport = i == methodsToOverride.length-1 ? fSnippetSupport : false;
				IMethodBinding curr = methodsToOverride[i];
				MethodDeclaration stub = StubUtility2Core.createImplementationStubCore(workingCopy, rewrite, importRewrite, null, curr, dummyTypeBinding, settings, dummyTypeBinding.isInterface(), focusNode, snippetSupport);
				rewriter.insertFirst(stub, null);
			}
			IDocument document = new Document(workingCopy.getSource());
			try {
				rewrite.rewriteAST().apply(document);
				int bodyStart = trackedDeclaration.getStartPosition() + dummyClassContent.indexOf('{');
				int bodyEnd = trackedDeclaration.getStartPosition() + trackedDeclaration.getLength();
				return document.get(bodyStart, bodyEnd - bodyStart);
			} catch (MalformedTreeException exception) {
				JavaLanguageServerPlugin.logException(exception.getMessage(), exception);
			} catch (BadLocationException exception) {
				JavaLanguageServerPlugin.logException(exception.getMessage(), exception);
			}
			return null;
		} finally {
			if (workingCopy != null) {
				workingCopy.discardWorkingCopy();
			}
		}
'''

text = '''
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            // Create channel to show notifications.
            String channelId  = getString(R.string.default_notification_channel_id);
            String channelName = getString(R.string.default_notification_channel_name);
            NotificationManager notificationManager =
                    getSystemService(NotificationManager.class);
            notificationManager.createNotificationChannel(new NotificationChannel(channelId,
                    channelName, NotificationManager.IMPORTANCE_LOW));
        }

        // If a notification message is tapped, any data accompanying the notification
        // message is available in the intent extras. In this sample the launcher
        // intent is fired when the notification is tapped, so any accompanying data would
        // be handled here. If you want a different intent fired, set the click_action
        // field of the notification message to the desired intent. The launcher intent
        // is used when no click_action is specified.
        //
        // Handle possible data accompanying notification message.
        // [START handle_data_extras]
        if (getIntent().getExtras() != null) {
            for (String key : getIntent().getExtras().keySet()) {
                Object value = getIntent().getExtras().get(key);
                Log.d(TAG, "Key: " + key + " Value: " + value);
            }
        }
        // [END handle_data_extras]

        Button subscribeButton = findViewById(R.id.subscribeButton);
        subscribeButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d(TAG, "Subscribing to weather topic");
                // [START subscribe_topics]
                FirebaseMessaging.getInstance().subscribeToTopic("weather")
                        .addOnCompleteListener(new OnCompleteListener<Void>() {
                            @Override
                            public void onComplete(@NonNull Task<Void> task) {
                                String msg = getString(R.string.msg_subscribed);
                                if (!task.isSuccessful()) {
                                    msg = getString(R.string.msg_subscribe_failed);
                                }
                                Log.d(TAG, msg);
                                Toast.makeText(MainActivity.this, msg, Toast.LENGTH_SHORT).show();
                            }
                        });
                // [END subscribe_topics]
            }
        });

        Button logTokenButton = findViewById(R.id.logTokenButton);
        logTokenButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Get token
                // [START retrieve_current_token]
                FirebaseInstanceId.getInstance().getInstanceId()
                        .addOnCompleteListener(new OnCompleteListener<InstanceIdResult>() {
                            @Override
                            public void onComplete(@NonNull Task<InstanceIdResult> task) {
                                if (!task.isSuccessful()) {
                                    Log.w(TAG, "getInstanceId failed", task.getException());
                                    return;
                                }

                                // Get new Instance ID token
                                String token = task.getResult().getToken();

                                // Log and toast
                                String msg = getString(R.string.msg_token_fmt, token);
                                Log.d(TAG, msg);
                                Toast.makeText(MainActivity.this, msg, Toast.LENGTH_SHORT).show();
                            }
                        });
                // [END retrieve_current_token]
            }
        });
    }
'''
import operator
from functools import reduce
import pandas as pd


def run_blocks(java_files_dir, csv_to_merge):
    df_merge = pd.read_csv(csv_to_merge)
    # df_merge = df_merge.drop(['Unnamed: 0'], axis=1)
    # df = pd.read_csv(file_csv)
    # df['File'] = df['filename']
    # df_index = df_merge.merge(df, on=['cyclo', 'ncss', 'File'])


    new_df = pd.DataFrame(columns=df_merge.columns)
    # df = df.drop('Unnamed: 0', axis=1)
    for _, row in df_merge.iterrows():
        try:
            filepath = row['File'].strip()
            p = Path(java_files_dir) / Path(filepath).stem
            blocks = []
            java_File = str(p) + '.java'
            with open(java_File) as f:
                text = f.read()
                lines = text.split('\n')
                start = row['start_line']
                ast = AST.build_from_javalang(build_ast(str(java_File)))
                method_node = [
                    x for x in ast.get_proxy_nodes(ASTNodeType.METHOD_DECLARATION,ASTNodeType.CONSTRUCTOR_DECLARATION)
                    if (x.name == row['method_name']) and (start == x.line)
                ][0]
                _, end = method_body_lines(method_node, text)
                src = lines[start:end-1]
                func_length = (end-1) - start
                for x in get_block_slices('\n'.join(src), LANG_JAVA):
                    diff = x[1][0] - x[0][0]
                    if (diff > 5) and (diff < (0.8 * func_length)):
                        # print(x[0][0] + 1 + start, x[1][0] + 1 + start)
                        blocks.append((x[0][0] + 1 + start, x[1][0] + 1 + start))
                        row['blocks'] = blocks
        except Exception as e:
            row['blocks'] = 'exception_happened'
            # print(p)
        new_df = new_df.append(row, ignore_index=True)

    new_df.to_csv(f'{Path(csv_to_merge).stem}_with_blocks.csv')


# run_blocks(r'D:/temp/dataset_colelction_refactoring/manual_validation_slices/small_slices/small_slices' ,r'C:\Users\e00533045\Downloads\methods_small_format.csv')
run_blocks(r'D:\temp\dataset_colelction_refactoring\manual_validation_slices\large_slices\java', r'C:\Users\e00533045\Downloads\methods_large.csv')
        # print()
    # code = '\n'.join(src)
    # print(code)
    # print('###############################')
    # for s1, s2, slice in get_complete_computation_slices(code, LANG_JAVA):
    #     print(s2.name)
    #     print(slice.get_slice_code())
    #     print(slice.get_ranges())
    #     print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')

    # # if s2.name == 'msg':
    #     print(f'func {s1.name} var {s2.name}')
    #     ranges = [list(range(x[0][0], x[1][0] + 1)) for x in slice.get_ranges()]
    #     lst = sorted(reduce(operator.concat, ranges))
    #     for x in lst:
    #         print(slice.code_lines[x])

    # print(f'func {s1.name} var {s2.name}')
    # print([(x[0][0], x[1][0]) for x in slice.get_ranges()])
