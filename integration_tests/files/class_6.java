/* Copyright (c) Huawei Technologies Co., Ltd. 2019-2020. All rights reserved. */

package com.huawei.codebot.analyzer.cxx.binder;

import static com.huawei.codebot.analyzer.cxx.hwconvention.throwexceptionreturn.SpecificFixerUtil.getFunctionDeclarationFirstLine;
import static com.huawei.codebot.analyzer.cxx.hwconvention.throwexceptionreturn.SpecificFixerUtil.specificLineBreak;

import com.huawei.codebot.analyzer.cxx.utils.CxxFileUtils;
import com.huawei.codebot.codeparsing.cxx.CxxCodeAnalyzer;
import com.huawei.codebot.codeparsing.cxx.PreprocessedFile;
import com.huawei.codebot.utils.FileUtils;
import com.huawei.codebot.utils.StringUtil;

import org.apache.commons.lang3.exception.ExceptionUtils;
import org.eclipse.cdt.core.dom.ast.ASTVisitor;
import org.eclipse.cdt.core.dom.ast.IASTCompoundStatement;
import org.eclipse.cdt.core.dom.ast.IASTDeclSpecifier;
import org.eclipse.cdt.core.dom.ast.IASTDeclaration;
import org.eclipse.cdt.core.dom.ast.IASTDeclarator;
import org.eclipse.cdt.core.dom.ast.IASTEnumerationSpecifier.IASTEnumerator;
import org.eclipse.cdt.core.dom.ast.IASTExpression;
import org.eclipse.cdt.core.dom.ast.IASTInitializer;
import org.eclipse.cdt.core.dom.ast.IASTName;
import org.eclipse.cdt.core.dom.ast.IASTNode;
import org.eclipse.cdt.core.dom.ast.IASTPreprocessorIncludeStatement;
import org.eclipse.cdt.core.dom.ast.IASTPreprocessorMacroDefinition;
import org.eclipse.cdt.core.dom.ast.IASTStatement;
import org.eclipse.cdt.core.dom.ast.IASTTranslationUnit;
import org.eclipse.cdt.core.dom.ast.cpp.ICPPASTCompositeTypeSpecifier;
import org.eclipse.cdt.core.dom.ast.cpp.ICPPASTCompositeTypeSpecifier.ICPPASTBaseSpecifier;
import org.eclipse.cdt.core.dom.ast.cpp.ICPPASTExpression;
import org.eclipse.cdt.core.dom.ast.cpp.ICPPASTParameterDeclaration;
import org.eclipse.cdt.core.parser.IToken;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTArraySubscriptExpression;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTBinaryExpression;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTCastExpression;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTCompositeTypeSpecifier;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTConditionalExpression;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTDeclarationStatement;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTDeleteExpression;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTEnumerationSpecifier;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTExpressionList;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTFieldReference;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTFunctionCallExpression;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTFunctionDeclarator;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTFunctionDefinition;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTIdExpression;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTLambdaExpression;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTLinkageSpecification;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTLiteralExpression;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTNamespaceDefinition;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTNewExpression;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTProblemDeclaration;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTProblemExpression;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTSimpleDeclaration;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTSimpleTypeConstructorExpression;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTTemplateDeclaration;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTTypeIdExpression;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTTypeIdInitializerExpression;
import org.eclipse.cdt.internal.core.dom.parser.cpp.CPPASTUnaryExpression;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.file.Paths;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 *  ??????cdt??????C/C++??????????????????????????????????????????Token
 *
 * @author wutianyong (w00429929)
 * @version 1.0
 * @since 2019???3???26???
 */
public class CxxFileDefAndRefParser {
    // logger
    private static final Logger logger = LoggerFactory.getLogger(CxxFileDefAndRefParser.class);

    /**
     * CxxFileInfo
     */
    public CxxFileInfo cxxFileInfo;

    // ????????????
    String filePath;

    public CxxFileDefAndRefParser() {}

    public CxxFileDefAndRefParser(String filePath) {
        this.filePath = filePath;
        cxxFileInfo = new CxxFileInfo(isHeaderFile(filePath));
    }

    /**
     * parseCustomizedFunctionDefinition
     *
     * @param functionDefinition ????????????????????????
     * @param className ??????
     * @param namespace ?????????namespace
     * @param cxxFileInfo cxxFileInfo??????
     * @return void
     */
    public void parseCustomizedFunctionDefinition(
            CPPASTFunctionDefinition functionDefinition, String className, String namespace, CxxFileInfo cxxFileInfo) {}

    /**
     * ????????????
     *
     * @param node ??????
     * param isReference
     * @return void
     */
    public void parseCustomizedProblemASTNode(IASTNode node, boolean isReference) {}

    /**
     * ?????????????????????????????????????????????Token
     *
     * @param filePath ????????????????????????
     * @return CodeFileInfo
     */
    public CxxFileInfo generateCodeFileInfo(String filePath) {
        // ????????????????????????????????????????????????
        String[] fileNameAndFolder = FileUtils.getFileNameAndDirectory(filePath);
        cxxFileInfo.fileName = fileNameAndFolder[0];
        cxxFileInfo.fileFolder = fileNameAndFolder[1];
        cxxFileInfo.filePath = Paths.get(cxxFileInfo.fileFolder, cxxFileInfo.fileName).normalize().toString();
        cxxFileInfo.offsetMap = calOffsetMap(filePath);

        // ?????????????????????????????????????????????Token
        try {
            // ??????cdt??????????????????TranslationUnit
            IASTTranslationUnit translationUnit = getTranslationUnit(filePath);

            // ??????include????????????????????????????????????
            parseIncludeStatements(translationUnit);

            // ?????????????????????
            parseMacroDefinitons(translationUnit);

            // ????????????/????????????, ????????????????????????????????????????????????????????????????????????
            parseDeclaration(translationUnit);
        } catch (Exception e) {
            // ????????????
            cxxFileInfo.parseFailed = true;
            logger.error(ExceptionUtils.getStackTrace(e));
        } catch (Error e) {
            // ????????????
            cxxFileInfo.parseFailed = true;
            cxxFileInfo.parseFailed = true;
            logger.error(ExceptionUtils.getStackTrace(e));
        }

        return cxxFileInfo;
    }

    /**
     * ??????cdt?????????????????????TranslationUnit
     *
     * @param filePath ????????????
     * @return TranslationUnit
     * @throws Exception
     */
    public IASTTranslationUnit getTranslationUnit(String filePath) throws Exception {
        PreprocessedFile processedFile = CxxCodeAnalyzer.preprocess(filePath, true);
        IASTTranslationUnit translationUnit = CxxCodeAnalyzer.getTranslationUnit(processedFile);
        return translationUnit;
    }

    /**
     * ??????include????????????????????????????????????
     *
     * @param translationUnit ????????????
     *
     */
    public void parseIncludeStatements(IASTTranslationUnit translationUnit) {
        IASTPreprocessorIncludeStatement[] preprocessorIncludeStatements = translationUnit.getIncludeDirectives();
        for (IASTPreprocessorIncludeStatement statement : preprocessorIncludeStatements) {
            HeaderFileRef headerFileRef = generateHeaderFileRef(statement);
            cxxFileInfo.headerFileRefList.add(headerFileRef);
        }
    }

    /**
     * ???????????????????????????????????????Token??????????????????????????????
     *
     * @param translationUnit TranslationUnit
     */
    public void parseMacroDefinitons(IASTTranslationUnit translationUnit) {
        // ??????????????????????????????
        IASTPreprocessorMacroDefinition[] macroDefinitions = translationUnit.getMacroDefinitions();

        // ??????
        for (IASTPreprocessorMacroDefinition macroDefinition : macroDefinitions) {
            // ???????????????Token?????????Token??????

            String sourceName = macroDefinition.getExpansion();

            IASTName destNameNode = macroDefinition.getName();
            String destName = destNameNode.getRawSignature();

            // ???Token -> ??????Token
            if (!sourceName.isEmpty()) {
                ReferenceToken sourceToken =
                        new ReferenceToken(
                                sourceName,
                                "",
                                "",
                                "",
                                TokenType.VARIABLE_REF,
                                macroDefinition.getExpansionLocation().getStartingLineNumber(),
                                macroDefinition.getExpansionLocation().getNodeOffset(),
                                cxxFileInfo);
                cxxFileInfo.addReference(sourceToken);
            }

            // ??????Token -> ??????Token
            DefinitionToken destToken =
                    new DefinitionToken(
                            destName,
                            "",
                            "",
                            TokenType.MACRO_DEF,
                            destNameNode.getFileLocation().getStartingLineNumber(),
                            destNameNode.getFileLocation().getNodeOffset(),
                            cxxFileInfo);
            cxxFileInfo.addDefinition(destToken);
        }
    }

    /**
     * ??????include???????????????????????????????????????
     *
     * @param statement statement
     * @return HeaderFileRef ?????????????????????
     */
    private HeaderFileRef generateHeaderFileRef(IASTPreprocessorIncludeStatement statement) {
        HeaderFileRef headerFileRef = new HeaderFileRef();

        // ?????????????????????????????????????????????????????????????????????????????????????????????
        headerFileRef.includeStatementRawSignature = statement.getRawSignature();
        headerFileRef.rawSignature = statement.getName().getRawSignature().trim();
        headerFileRef.startLineNum = statement.getFileLocation().getStartingLineNumber();
        headerFileRef.codeFileInfo = cxxFileInfo;
        String[] fileNameAndDirectory = FileUtils.getFileNameAndDirectory(headerFileRef.rawSignature);
        headerFileRef.fileName = fileNameAndDirectory[0];
        headerFileRef.relativeFolder = formatRelativeFolder(fileNameAndDirectory[1]);

        return headerFileRef;
    }

    /**
     * ?????????include?????????????????????????????????
     *
     * @param folder ???????????????
     * @return ??????????????????????????????
     */
    private String formatRelativeFolder(String folder) {
        String fileSeperator = "/";
        if (folder.contains("\\")) {
            fileSeperator = "\\";
        }
        return folder.replace(".." + fileSeperator, "").replace("..", "");
    }

    /**
     * ????????????/????????????, ????????????????????????????????????????????????????????????????????????
     *
     * @param translationUnit ????????????
     *
     */
    private void parseDeclaration(IASTTranslationUnit translationUnit) {
        IASTDeclaration[] astDecs = translationUnit.getDeclarations();
        for (IASTDeclaration dec : astDecs) {
            parseDeclaration(dec, "", "");
        }
    }

    /**
     * ??????????????????????????????????????????????????????Token??????????????????????????????
     *
     * @param declaration ???????????????????????????AST??????
     * @param className ??????AST??????????????????
     * @param namespace ??????AST????????????namespace
     */
    public void parseDeclaration(IASTDeclaration declaration, String className, String namespace) {
        if (declaration instanceof CPPASTNamespaceDefinition) {
            // ???AST?????????namespace??????
            parseNamespaceDefinition((CPPASTNamespaceDefinition) declaration, namespace);
        } else if (declaration instanceof CPPASTSimpleDeclaration) {
            // ???AST????????????/?????????/?????????/??????/?????????????????????
            parseSimpleDeclaration((CPPASTSimpleDeclaration) declaration, className, namespace);
        } else if (declaration instanceof CPPASTFunctionDefinition) {
            // ???AST?????????????????????
            parseFunctionDefinition((CPPASTFunctionDefinition) declaration, className, namespace);
            parseCustomizedFunctionDefinition(
                    (CPPASTFunctionDefinition) declaration, className, namespace, cxxFileInfo);
        } else if (declaration instanceof CPPASTTemplateDeclaration) {
            // ???AST?????????Template??????
            parseTemplateDeclaration((CPPASTTemplateDeclaration) declaration, className, namespace);
        } else if (declaration instanceof CPPASTLinkageSpecification) {
            // ???AST?????????extern "C"??????
            CPPASTLinkageSpecification ls = (CPPASTLinkageSpecification) declaration;
            for (IASTDeclaration subDeclaration : ls.getDeclarations()) {
                parseDeclaration(subDeclaration, className, namespace);
            }
        } else {
            if (declaration instanceof CPPASTProblemDeclaration) {
                // ???????????????????????????Token
                CPPASTProblemDeclaration problemDeclaration = (CPPASTProblemDeclaration) declaration;
                for (IASTNode node : problemDeclaration.getChildren()) {
                    parseProblemASTNode(node, true);
                }
            }
        }
    }

    /**
     * ??????namespace????????????????????????????????????Token??????????????????????????????
     *
     * @param namespaceDefinition namespace??????AST??????
     * @param namespace ??????AST????????????namespace?????????namespace?????????.??????
     */
    private void parseNamespaceDefinition(CPPASTNamespaceDefinition namespaceDefinition, String namespace) {
        // ??????namespace
        String currentNamespaceName = namespaceDefinition.getName().toString();
        String fullNamesapceName = currentNamespaceName;
        if (!namespace.equals("")) {
            fullNamesapceName = namespace + "." + currentNamespaceName;
        }
        if (currentNamespaceName.equals("")) {
            fullNamesapceName = namespace;
        }

        // ?????????????????????
        IASTDeclaration[] declarations = namespaceDefinition.getDeclarations();
        for (IASTDeclaration subDeclaration : declarations) {
            parseDeclaration(subDeclaration, "", fullNamesapceName);
        }
    }

    /**
     * ????????????????????????????????????????????????Token??????????????????????????????
     *
     * @param simpleDeclaration ??????????????????AST??????
     * @param className ??????AST??????????????????
     * @param namespace ??????AST????????????namespace
     */
    private void parseSimpleDeclaration(CPPASTSimpleDeclaration simpleDeclaration, String className, String namespace) {
        CPPASTCompositeTypeSpecifier typeSpecifier = isClassDeclaration(simpleDeclaration);
        if (typeSpecifier != null) {
            // ???????????????/?????????/?????????????????????
            parseClassDeclaration(simpleDeclaration, typeSpecifier, namespace);
        } else if (simpleDeclaration.getDeclSpecifier() instanceof CPPASTEnumerationSpecifier) {
            // ??????????????????????????????
            parseEnumDeclaration(simpleDeclaration, className, namespace);
        } else {
            // ????????????typedef/????????????/??????????????????

            // ?????????????????????????????????????????????????????????
            String type = "";
            if (simpleDeclaration.getDeclSpecifier() != null) {
                type = simpleDeclaration.getDeclSpecifier().getRawSignature();
            }
            type = formatType(type);

            // ??????????????????
            String patternStr = "class[ \t]";
            Pattern pattern = Pattern.compile(patternStr);
            Matcher matcher = pattern.matcher(type);
            if (matcher.find()) {
                type = type.replaceFirst("class", "").trim();
                // ??????????????????????????????Token
                DefinitionToken token =
                        new DefinitionToken(
                                type,
                                type,
                                namespace,
                                TokenType.CLASS_FORWARD_DEC,
                                simpleDeclaration.getFileLocation().getStartingLineNumber(),
                                simpleDeclaration.getFileLocation().getNodeOffset(),
                                cxxFileInfo);
                cxxFileInfo.addDefinition(token);
            }

            // ??????????????????
            for (IASTDeclarator declarator : simpleDeclaration.getDeclarators()) {
                if (declarator instanceof CPPASTFunctionDeclarator) {
                    // ????????????
                    parseFunctionDeclarator((CPPASTFunctionDeclarator) declarator, type, className, namespace, true);
                } else if (type.startsWith("typedef")) {
                    // typedef
                    parseTypedefDeclarator(simpleDeclaration, declarator, className, namespace);
                } else {
                    // ????????????
                    parseFieldDeclarator(declarator, type, className, namespace);
                }
            }
        }
    }

    /**
     * ?????????????????????????????????????????????Token??????????????????????????????
     *
     * @param simpleDeclaration ??????????????????AST??????
     * @param typeSpecifier ????????????
     * @param namespace ??????AST????????????namespace
     */
    private void parseClassDeclaration(
            CPPASTSimpleDeclaration simpleDeclaration, CPPASTCompositeTypeSpecifier typeSpecifier, String namespace) {
        // ????????????
        String className = typeSpecifier.getName().toString();
        if (!className.isEmpty()) {
            // ????????????????????????Token
            DefinitionToken token =
                    new DefinitionToken(
                            className,
                            className,
                            namespace,
                            TokenType.CLASS_DEF,
                            typeSpecifier.getName().getFileLocation().getStartingLineNumber(),
                            typeSpecifier.getName().getFileLocation().getNodeOffset(),
                            cxxFileInfo);
            cxxFileInfo.addDefinition(token);
        }

        // ?????????????????????
        if (typeSpecifier.getBaseSpecifiers() != null && typeSpecifier.getBaseSpecifiers().length > 0) {
            for (int i = 0; i < typeSpecifier.getBaseSpecifiers().length; i++) {
                ICPPASTBaseSpecifier baseSpec = typeSpecifier.getBaseSpecifiers()[i];
                // ????????????????????????
                String fullParentName = baseSpec.getNameSpecifier().getRawSignature().replace("::", ".");

                // ????????????namespace?????????
                if (!namespace.equals("")) {
                    fullParentName = namespace + "." + fullParentName;
                }
                int index = fullParentName.lastIndexOf(".");
                String parentClassName = fullParentName;
                String parentNamespace = "";
                if (index >= 0) {
                    parentClassName = fullParentName.substring(index + 1);
                    parentNamespace = fullParentName.substring(0, index);
                }

                // ????????????????????????Token
                ReferenceToken token2 =
                        new ReferenceToken(
                                parentClassName,
                                parentClassName,
                                parentNamespace,
                                "",
                                TokenType.CLASS_REF,
                                baseSpec.getFileLocation().getStartingLineNumber(),
                                baseSpec.getFileLocation().getNodeOffset(),
                                cxxFileInfo);
                cxxFileInfo.addReference(token2);
            }
        }

        if (!className.isEmpty()) {
            // ???????????????????????????????????????
            for (IASTDeclaration member : typeSpecifier.getMembers()) {
                parseDeclaration(member, className, namespace);
            }
        }

        // ???????????????typedef??????
        if (simpleDeclaration.getRawSignature().startsWith("typedef")) {
            // ??????typedef???????????????
            String destName = "";
            if (simpleDeclaration.getDeclarators().length > 0 && simpleDeclaration.getDeclarators()[0] != null) {
                destName = simpleDeclaration.getDeclarators()[0].getRawSignature();
            }
            if (!destName.isEmpty()) {
                DefinitionToken token =
                        new DefinitionToken(
                                destName,
                                destName,
                                namespace,
                                TokenType.CLASS_DEF,
                                simpleDeclaration.getDeclarators()[0].getFileLocation().getStartingLineNumber(),
                                simpleDeclaration.getDeclarators()[0].getFileLocation().getNodeOffset(),
                                cxxFileInfo);
                cxxFileInfo.addDefinition(token);
            }

            // ???????????????????????????????????????
            for (IASTDeclaration member : typeSpecifier.getMembers()) {
                parseDeclaration(member, destName, namespace);
            }
        }
    }

    /**
     * ??????????????????????????????????????????????????????Token??????????????????????????????
     *
     * @param simpleDeclaration ??????????????????AST??????
     * @param className ??????AST??????????????????
     * @param inputNameSpace ??????AST????????????namespace
     */
    private void parseEnumDeclaration(CPPASTSimpleDeclaration simpleDeclaration,
        String className, String inputNameSpace) {
        String namespace = inputNameSpace;
        // ??????namespace
        if (!className.equals("")) {
            if (namespace.equals("")) {
                namespace = className;
            } else {
                namespace += "." + className;
            }
        }

        // ????????????
        CPPASTEnumerationSpecifier enumerationSpecifier =
                (CPPASTEnumerationSpecifier) simpleDeclaration.getDeclSpecifier();
        String enumClassName = enumerationSpecifier.getName().toString();

        // ????????????????????????Token
        DefinitionToken token = null;
        if (!enumClassName.equals("")) {
            token =
                    new DefinitionToken(
                            enumClassName,
                            enumClassName,
                            namespace,
                            TokenType.CLASS_DEF,
                            enumerationSpecifier.getName().getFileLocation().getStartingLineNumber(),
                            enumerationSpecifier.getName().getFileLocation().getNodeOffset(),
                            cxxFileInfo);
            cxxFileInfo.addDefinition(token);
        }

        // ????????????????????????
        for (IASTDeclarator declarator : simpleDeclaration.getDeclarators()) {
            parseFieldDeclarator(declarator, enumClassName, className, namespace);
        }

        // ????????????????????????
        for (IASTEnumerator enumerator : enumerationSpecifier.getEnumerators()) {
            // ????????????????????????Token
            token =
                    new DefinitionToken(
                            enumerator.getName().toString(),
                            enumClassName,
                            namespace,
                            TokenType.VARIABLE_DEF,
                            enumerator.getFileLocation().getStartingLineNumber(),
                            enumerator.getFileLocation().getNodeOffset(),
                            cxxFileInfo);
            cxxFileInfo.addDefinition(token);
        }

        // ???????????????typedef??????
        if (simpleDeclaration.getRawSignature().startsWith("typedef")) {
            // ??????typedef???????????????
            String destName = "";
            if (simpleDeclaration.getDeclarators().length > 0 && simpleDeclaration.getDeclarators()[0] != null) {
                destName = simpleDeclaration.getDeclarators()[0].getRawSignature();
            }
            if (!destName.isEmpty()) {
                token =
                        new DefinitionToken(
                                destName,
                                destName,
                                namespace,
                                TokenType.CLASS_DEF,
                                simpleDeclaration.getDeclarators()[0].getFileLocation().getStartingLineNumber(),
                                simpleDeclaration.getDeclarators()[0].getFileLocation().getNodeOffset(),
                                cxxFileInfo);
                cxxFileInfo.addDefinition(token);
            }

            // ????????????????????????
            for (IASTDeclarator declarator : simpleDeclaration.getDeclarators()) {
                parseFieldDeclarator(declarator, enumClassName, className, namespace);
            }

            // ????????????????????????
            for (IASTEnumerator enumerator : enumerationSpecifier.getEnumerators()) {
                // ????????????????????????Token
                token =
                        new DefinitionToken(
                                enumerator.getName().toString(),
                                enumClassName,
                                namespace,
                                TokenType.VARIABLE_DEF,
                                enumerator.getFileLocation().getStartingLineNumber(),
                                enumerator.getFileLocation().getNodeOffset(),
                                cxxFileInfo);
                cxxFileInfo.addDefinition(token);
            }
        }
    }

    /**
     * ????????????????????????????????????????????????Token??????????????????????????????
     *
     * @param functionDefinition ??????????????????AST??????
     * @param className ??????AST??????????????????
     * @param namespace ??????AST????????????namespace
     */
    private void parseFunctionDefinition(
            CPPASTFunctionDefinition functionDefinition, String className, String namespace) {
        // ???????????????????????????
        IASTDeclSpecifier declSpecifier = functionDefinition.getDeclSpecifier();
        String type = "";
        if (declSpecifier != null) {
            type = declSpecifier.getRawSignature();
        }
        type = formatType(type);

        // ????????????????????????
        parseFunctionDeclarator(
                (CPPASTFunctionDeclarator) functionDefinition.getDeclarator(), type, className, namespace, false);

        // ???????????????
        parseFunctionBody(functionDefinition.getBody());
    }

    /**
     * ????????????????????????????????????????????????Token??????????????????????????????
     *
     * @param functionDeclarator ??????????????????AST??????
     * @param inputClassName ??????AST??????????????????
     * @param namespace ??????AST????????????namespace
     * @param isFunctionDeclaration ?????????????????????
     */
    private void parseFunctionDeclarator(
            CPPASTFunctionDeclarator functionDeclarator,
            String inputType,
            String inputClassName,
            String namespace,
            boolean isFunctionDeclaration) {
        String className = inputClassName;
        // ???????????????
        String functionName = functionDeclarator.getName().getLastName().toString();
        if (functionName.equals("")) {
            IASTDeclarator declarator = functionDeclarator.getNestedDeclarator();
            if (declarator != null) {
                functionName = declarator.getName().getRawSignature();
            }
        }

        // ????????????????????????
        if (className.equals("")) {
            String fullFunctionName = functionDeclarator.getName().toString();
            int index = fullFunctionName.lastIndexOf("::");
            if (index > 0) {
                className = fullFunctionName.substring(0, index);
            }
        }

        // ????????????????????????Token
        TokenType tokenType = TokenType.FUNCTION_DEF;
        if (isFunctionDeclaration) {
            tokenType = TokenType.FUNCTION_DEC;
        }
        String declarationContent =
                getFunctionDeclarationFirstLine(
                        functionDeclarator, functionDeclarator.getFileLocation().getStartingLineNumber());
        DefinitionToken token =
                new DefinitionToken(
                        functionName,
                        className,
                        namespace,
                        tokenType,
                        functionDeclarator.getFileLocation().getStartingLineNumber(),
                        functionDeclarator.getFileLocation().getNodeOffset(),
                        cxxFileInfo);
        token.setDeclarationContent(declarationContent);
        cxxFileInfo.addDefinition(token);

        // ??????????????????????????????????????????Token
        String type = inputType;
        if (!type.isEmpty()) {
            type = formatType(type);
            ReferenceToken token2 =
                    new ReferenceToken(
                            type,
                            type,
                            Constant.UNKNOWN,
                            "",
                            TokenType.CLASS_REF,
                            functionDeclarator.getFileLocation().getStartingLineNumber(),
                            functionDeclarator.getFileLocation().getNodeOffset(),
                            cxxFileInfo);
            cxxFileInfo.addReference(token2);
        }

        // ??????????????????
        for (ICPPASTParameterDeclaration parameterDeclaration : functionDeclarator.getParameters()) {
            // ????????????????????????
            String paramType = formatType(getParameterType(parameterDeclaration));
            // ????????????????????????Token
            ReferenceToken token2 =
                    new ReferenceToken(
                            paramType,
                            paramType,
                            Constant.UNKNOWN,
                            "",
                            TokenType.CLASS_REF,
                            parameterDeclaration.getFileLocation().getStartingLineNumber(),
                            parameterDeclaration.getFileLocation().getNodeOffset(),
                            cxxFileInfo);
            cxxFileInfo.addReference(token2);
        }
    }

    /**
     * ???????????????????????????????????????Token??????????????????????????????
     *
     * @param body ????????????AST??????
     */
    private void parseFunctionBody(IASTStatement body) {
        if (body != null) {
            body.accept(new FunctionBodyVisitor(cxxFileInfo));
        }
    }

    /**
     * ????????????????????????????????????????????????Token??????????????????????????????
     *
     * @param declarator ???????????????AST??????
     * @param type ????????????
     * @param className ??????AST??????????????????
     * @param namespace ??????AST????????????namespace
     */
    private void parseFieldDeclarator(IASTDeclarator declarator, String type, String className, String namespace) {
        // ???????????????
        String varName = declarator.getName().toString();

        if (varName.isEmpty()) {
            // ????????????????????????????????????????????????????????????
            ReferenceToken token =
                    new ReferenceToken(
                            type,
                            Constant.UNKNOWN,
                            Constant.UNKNOWN,
                            "",
                            TokenType.UNKNOWN,
                            declarator.getFileLocation().getStartingLineNumber(),
                            declarator.getFileLocation().getNodeOffset(),
                            cxxFileInfo);
            cxxFileInfo.addReference(token);
            // ????????????token
            parseProblemASTNode(declarator, true);
        } else {
            // ??????????????????Token
            DefinitionToken token =
                    new DefinitionToken(
                            varName,
                            className,
                            namespace,
                            TokenType.VARIABLE_DEF,
                            declarator.getFileLocation().getStartingLineNumber(),
                            declarator.getFileLocation().getNodeOffset(),
                            cxxFileInfo);
            cxxFileInfo.addDefinition(token);
        }

        // ?????????????????????
        IASTInitializer initializer = declarator.getInitializer();
        if (initializer != null) {
            initializer.accept(new FunctionBodyVisitor(cxxFileInfo));
        }
    }

    /**
     * ??????typedef??????????????????????????????Token??????????????????????????????
     *
     * @param simpleDeclaration ??????????????????AST??????
     * @param declarator ???????????????
     * @param className ??????AST??????????????????
     * @param namespace ??????AST????????????namespace
     */
    private void parseTypedefDeclarator(
            CPPASTSimpleDeclaration simpleDeclaration, IASTDeclarator declarator, String className, String namespace) {
        // ??????typedef?????????
        String type;
        if (simpleDeclaration.getDeclSpecifier().getChildren().length > 0) {
            type = simpleDeclaration.getDeclSpecifier().getChildren()[0].getRawSignature();
        } else {
            type = simpleDeclaration.getDeclSpecifier().getRawSignature().substring(7).trim();
        }
        ReferenceToken token =
                new ReferenceToken(
                        type,
                        type,
                        "",
                        "",
                        TokenType.CLASS_REF,
                        simpleDeclaration.getFileLocation().getStartingLineNumber(),
                        simpleDeclaration.getFileLocation().getNodeOffset(),
                        cxxFileInfo);
        cxxFileInfo.addReference(token);

        // ??????typedef??????????????????????????????????????????
        parseProblemASTNode(declarator, false);
    }

    /**
     * ??????template??????????????????????????????Token??????????????????????????????
     *
     * @param templateDeclaration template??????AST??????
     * @param className ??????AST??????????????????
     * @param namespace ??????AST????????????namespace
     */
    private void parseTemplateDeclaration(
            CPPASTTemplateDeclaration templateDeclaration, String className, String namespace) {}

    /**
     * ?????????????????????????????????????????????Token??????????????????????????????
     *
     * @param node AST??????
     *            ??????????????????
     * @param isReference  ???????????????token
     */
    public void parseProblemASTNode(IASTNode node, boolean isReference) {
        try {
            int startOffset = node.getNodeLocations()[0].getNodeOffset();
            IToken token = node.getSyntax();
            while (token != null) {
                // ?????????identifier???token
                if (token.getType() != IToken.tIDENTIFIER) {
                    token = token.getNext();
                    continue;
                }

                // ??????token???
                String tokenStr = new String(token.getCharImage());
                int tokenStartOffset = startOffset + token.getOffset();
                int startLineNum = cxxFileInfo.getStartLineNumberByOffset(tokenStartOffset);

                // ??????Token
                if (isReference) {
                    ReferenceToken referenceToken =
                            new ReferenceToken(
                                    tokenStr,
                                    Constant.UNKNOWN,
                                    Constant.UNKNOWN,
                                    "",
                                    TokenType.UNKNOWN,
                                    startLineNum,
                                    tokenStartOffset,
                                    cxxFileInfo);
                    cxxFileInfo.addReference(referenceToken);
                } else {
                    DefinitionToken definitionToken =
                            new DefinitionToken(
                                    tokenStr,
                                    Constant.UNKNOWN,
                                    Constant.UNKNOWN,
                                    TokenType.UNKNOWN,
                                    startLineNum,
                                    tokenStartOffset,
                                    cxxFileInfo);
                    cxxFileInfo.addDefinition(definitionToken);
                }

                // next
                token = token.getNext();
            }
        } catch (Exception e) {
            logger.error(e.getMessage());
        }
    }

    /**
     * ??????AST??????????????????????????????/????????????????????????
     *
     * @param simpleDeclaration ??????????????????AST??????
     * @return CPPASTCompositeTypeSpecifier??????????????????????????????????????????null
     */
    private CPPASTCompositeTypeSpecifier isClassDeclaration(CPPASTSimpleDeclaration simpleDeclaration) {
        if (simpleDeclaration.getDeclSpecifier() instanceof CPPASTCompositeTypeSpecifier) {
            CPPASTCompositeTypeSpecifier compositeTypeSpec =
                    (CPPASTCompositeTypeSpecifier) simpleDeclaration.getDeclSpecifier();
            if (compositeTypeSpec.getKey() == ICPPASTCompositeTypeSpecifier.k_class
                    || compositeTypeSpec.getKey() == ICPPASTCompositeTypeSpecifier.k_struct
                    || compositeTypeSpec.getKey() == ICPPASTCompositeTypeSpecifier.k_union) {
                return compositeTypeSpec;
            }
        }
        return null;
    }

    /**
     * ????????????????????????
     *
     * @param parameterDeclaration ??????????????????AST??????
     * @return ??????????????????
     */
    private String getParameterType(ICPPASTParameterDeclaration parameterDeclaration) {
        String type = "";
        if (parameterDeclaration.getDeclSpecifier() != null) {
            type = parameterDeclaration.getDeclSpecifier().getRawSignature();
        }
        if (type.endsWith(" const")) {
            type = type.substring(0, type.lastIndexOf(" "));
        }
        if (type.startsWith("const ")) {
            type = type.substring(type.indexOf(" ") + 1);
        }
        return type;
    }

    /**
     * ??????????????????????????????????????????namespace
     *
     * @param type ???????????????
     * @return {??????, namespace}
     */
    public static String[] getClassAndNamespace(String type) {
        String className;
        String namespace;

        int index = type.lastIndexOf("::");
        if (index >= 0) {
            namespace = type.substring(0, index).replace("::", ".");
            className = type.substring(index + 2, type.length());
        } else {
            className = type;
            namespace = Constant.UNKNOWN;
        }
        return new String[] {className, namespace};
    }

    /**
     * ??????????????????????????????????????????
     *
     * @param type ???????????????
     * @return ?????????????????????
     */
    private static String formatType(String type) {
        return type.replace("virtual ", "")
                .replace("static ", "")
                .replace("const ", "")
                .replace("struct", "")
                .replace("typedef", "")
                .trim();
    }

    /**
     * ????????????????????????????????????
     *
     * @param filePath ????????????
     * @return ????????????true??????????????????false
     */
    private boolean isHeaderFile(String filePath) {
        return FileUtils.isValidExtension(filePath, Constant.HEADER_FILE_EXTENSION);
    }

    /**
     * ??????offset????????????????????????
     *
     * @param filePath ????????????
     * @return offset????????????????????????
     */
    private int[][] calOffsetMap(String filePath) {
        try {
            String fileContent = CxxFileUtils.preprocessFile(filePath);
            String lineBreak = StringUtil.getLineBreak(fileContent);
            specificLineBreak = lineBreak;
            int lineBreakLength = lineBreak.length();
            String[] lines = fileContent.split(lineBreak);
            int[][] offsetMap = new int[lines.length][2];
            int offset = 0;
            for (int i = 0; i < lines.length; i++) {
                String line = lines[i];
                offsetMap[i][0] = offset;
                offsetMap[i][1] = offset + line.length() + lineBreakLength - 1;
                offset = offsetMap[i][1] + 1;
            }
            return offsetMap;
        } catch (Exception e) {
            logger.error("Fail to preprocessed file  {}", filePath);
        }
        return null;
    }

    /**
     * ??????????????????
     *
     * @author z00484120
     * @since 3.0.0
     */
    public class FunctionBodyVisitor extends ASTVisitor {
        // ??????????????????
        CxxFileInfo cxxFileInfo;

        // ????????????????????????????????????????????????scope??????????????????????????????????????????
        LinkedList<HashMap<String, VariableInfo>> variableMaps;

        public FunctionBodyVisitor(CxxFileInfo cxxFileInfo) {
            this.cxxFileInfo = cxxFileInfo;
            this.shouldVisitExpressions = true;
            this.shouldVisitStatements = true;
            variableMaps = new LinkedList<>();
        }

        @Override
        public int visit(IASTStatement statement) {
            if (statement instanceof CPPASTDeclarationStatement) {
                // ??????????????????
                CPPASTDeclarationStatement declarationStatement = (CPPASTDeclarationStatement) statement;
                if (declarationStatement.getDeclaration() instanceof CPPASTSimpleDeclaration) {
                    CPPASTSimpleDeclaration simpleDeclaration =
                            (CPPASTSimpleDeclaration) declarationStatement.getDeclaration();

                    // ??????????????????
                    String type = "";
                    if (simpleDeclaration.getDeclSpecifier() != null) {
                        type = simpleDeclaration.getDeclSpecifier().getRawSignature();
                    }
                    type = formatType(type);
                    String[] classAndNamespace = getClassAndNamespace(type);

                    // ???????????????
                    IASTDeclarator[] astDecs = simpleDeclaration.getDeclarators();
                    // traverse declarator array
                    for (IASTDeclarator declarator : astDecs) {
                        // local variable declaration
                        String varName = declarator.getName().toString();
                        variableMaps
                                .getFirst()
                                .put(
                                        varName,
                                        new VariableInfo(
                                                classAndNamespace[0],
                                                classAndNamespace[1],
                                                declarator.getFileLocation().getStartingLineNumber(),
                                                declarator.getFileLocation().getNodeOffset()));
                    }
                }

            } else {
                if (statement instanceof IASTCompoundStatement) {
                    // ????????????
                    HashMap<String, VariableInfo> map;
                    if (variableMaps.size() > 0) {
                        map = new HashMap<>(variableMaps.getFirst());
                    } else {
                        map = new HashMap<>();
                    }
                    variableMaps.addFirst(map);
                }
            }
            return super.visit(statement);
        }

        @Override
        public int leave(IASTStatement statement) {
            if (statement instanceof IASTCompoundStatement) {
                Map<String, VariableInfo> m = variableMaps.removeFirst();
                for (Map.Entry<String, VariableInfo> entry : m.entrySet()) {
                    VariableInfo variableInfo = entry.getValue();
                    String className = variableInfo.className;
                    String namespace = variableInfo.namespace;
                    int startLineNumber = variableInfo.startLineNumber;
                    int startOffset = variableInfo.startOffset;
                    ReferenceToken token =
                            new ReferenceToken(
                                    className,
                                    className,
                                    namespace,
                                    "",
                                    TokenType.CLASS_REF,
                                    startLineNumber,
                                    startOffset,
                                    cxxFileInfo);
                    cxxFileInfo.addReference(token);
                }
            }
            return super.leave(statement);
        }

        @Override
        public int visit(IASTExpression expression) {
            if (expression instanceof CPPASTIdExpression) {
                visitIdExpression((CPPASTIdExpression) expression);
            } else if (expression instanceof CPPASTFunctionCallExpression) {
                visitFunctionCallExpression((CPPASTFunctionCallExpression) expression);
            } else if (expression instanceof CPPASTFieldReference) {
                visitFieldReference((CPPASTFieldReference) expression);
            } else if (expression instanceof CPPASTNewExpression) {
                visitNewExpression((CPPASTNewExpression) expression);
            } else if (expression instanceof CPPASTTypeIdExpression) {
                visitTypeIdExpression((CPPASTTypeIdExpression) expression);
            } else if (expression instanceof CPPASTProblemExpression) {
                parseProblemASTNode(expression, true);
            } else if (expression instanceof CPPASTBinaryExpression
                    || expression instanceof CPPASTUnaryExpression
                    || expression instanceof CPPASTLiteralExpression
                    || expression instanceof CPPASTArraySubscriptExpression
                    || expression instanceof CPPASTExpressionList
                    || expression instanceof CPPASTDeleteExpression
                    || expression instanceof CPPASTConditionalExpression
                    || expression instanceof CPPASTCastExpression
                    || expression instanceof CPPASTSimpleTypeConstructorExpression
                    || expression instanceof CPPASTLambdaExpression
                    || expression instanceof CPPASTTypeIdInitializerExpression) {
            } else {
            }
            return super.visit(expression);
        }

        private void visitIdExpression(CPPASTIdExpression expression) {
            String varName = expression.getName().getRawSignature();
            if (expression.getFileLocation() != null
                    && (variableMaps.size() == 0 || !variableMaps.getFirst().containsKey(varName))) {
                ReferenceToken token =
                        new ReferenceToken(
                                varName,
                                Constant.UNKNOWN,
                                Constant.UNKNOWN,
                                "",
                                TokenType.VARIABLE_REF,
                                expression.getFileLocation().getStartingLineNumber(),
                                expression.getFileLocation().getNodeOffset(),
                                cxxFileInfo);
                cxxFileInfo.addReference(token);
            }
        }

        private void visitFunctionCallExpression(CPPASTFunctionCallExpression expression) {
            // visit function name
            IASTExpression functionNameExpression = expression.getFunctionNameExpression();
            String methodName;
            String ownerName = "";
            String className = Constant.UNKNOWN;
            String namespace = Constant.UNKNOWN;

            if (functionNameExpression instanceof CPPASTIdExpression) {
                CPPASTIdExpression idExpression = (CPPASTIdExpression) functionNameExpression;
                String idStr = idExpression.toString();
                int startOffset = idExpression.getFileLocation().getNodeOffset();
                int index = idStr.lastIndexOf("::");
                if (index > 0) {
                    String str = idStr.substring(0, index).replace("::", ".");
                    methodName = idStr.substring(index + 2, idStr.length());
                    ownerName = str.replace("::", ".");
                    startOffset = startOffset + index + 2;
                } else {
                    methodName = idStr;
                }
                ReferenceToken token =
                        new ReferenceToken(
                                methodName,
                                className,
                                namespace,
                                ownerName,
                                TokenType.FUNCTION_REF,
                                idExpression.getFileLocation().getStartingLineNumber(),
                                startOffset,
                                cxxFileInfo);
                cxxFileInfo.addReference(token);
            } else {
                if (functionNameExpression instanceof CPPASTFieldReference) {
                    CPPASTFieldReference fieldReference = (CPPASTFieldReference) functionNameExpression;
                    methodName = fieldReference.getFieldName().getRawSignature();
                    ICPPASTExpression ownerExpression = fieldReference.getFieldOwner();
                    if (ownerExpression instanceof CPPASTIdExpression) {
                        ownerName = ownerExpression.getRawSignature();
                        if (variableMaps.size() > 0 && variableMaps.getFirst().containsKey(ownerName)) {
                            VariableInfo variableInfo = variableMaps.getFirst().get(ownerName);
                            className = variableInfo.className;
                            namespace = variableInfo.namespace;
                        }
                        ReferenceToken token =
                                new ReferenceToken(
                                        methodName,
                                        className,
                                        namespace,
                                        ownerName,
                                        TokenType.FUNCTION_REF,
                                        fieldReference.getFileLocation().getStartingLineNumber(),
                                        fieldReference.getFieldName().getFileLocation().getNodeOffset(),
                                        cxxFileInfo);
                        cxxFileInfo.addReference(token);
                    }
                }
            }
        }

        private void visitFieldReference(CPPASTFieldReference fieldReference) {
            if (fieldReference.getParent() instanceof CPPASTFunctionCallExpression) {
                return;
            }
            String varName = fieldReference.getFieldName().getRawSignature();
            String className = Constant.UNKNOWN;
            String namespace = Constant.UNKNOWN;
            ICPPASTExpression ownerExpression = fieldReference.getFieldOwner();
            if (ownerExpression instanceof CPPASTIdExpression && ownerExpression.getFileLocation() != null) {
                String ownerName = ownerExpression.getRawSignature();
                if (variableMaps.size() > 0 && variableMaps.getFirst().containsKey(ownerName)) {
                    VariableInfo variableInfo = variableMaps.getFirst().get(ownerName);
                    className = variableInfo.className;
                    namespace = variableInfo.namespace;
                }
                ReferenceToken token =
                        new ReferenceToken(
                                varName,
                                className,
                                namespace,
                                ownerName,
                                TokenType.VARIABLE_REF,
                                ownerExpression.getFileLocation().getStartingLineNumber(),
                                ownerExpression.getFileLocation().getNodeOffset(),
                                cxxFileInfo);
                cxxFileInfo.addReference(token);
            }
        }

        private void visitNewExpression(CPPASTNewExpression newExpression) {
            String idStr = newExpression.getTypeId().getRawSignature();
            String className = idStr;
            String namespace = Constant.UNKNOWN;

            if (className.endsWith("]")) {
                className = className.substring(0, className.indexOf('['));
            }
            if (className.endsWith("*")) {
                return;
            }
            int index = idStr.lastIndexOf("::");
            if (index > 0) {
                String str = idStr.substring(0, index);
                namespace = str.replace("::", ".");
                className = idStr.substring(index + 2, idStr.length());
            }

            ReferenceToken token =
                    new ReferenceToken(
                            className,
                            className,
                            namespace,
                            "",
                            TokenType.CLASS_REF,
                            newExpression.getFileLocation().getStartingLineNumber(),
                            newExpression.getTypeId().getFileLocation().getNodeOffset(),
                            cxxFileInfo);
            cxxFileInfo.addReference(token);
        }

        private void visitTypeIdExpression(CPPASTTypeIdExpression typeIdExpression) {
            if (typeIdExpression.getOperator() == CPPASTTypeIdExpression.op_sizeof) {
                String type = typeIdExpression.getChildren()[0].getRawSignature();
                String[] classAndNamespace = getClassAndNamespace(type);
                ReferenceToken token =
                        new ReferenceToken(
                                classAndNamespace[0],
                                classAndNamespace[0],
                                classAndNamespace[1],
                                "",
                                TokenType.CLASS_REF,
                                typeIdExpression.getFileLocation().getStartingLineNumber(),
                                typeIdExpression.getFileLocation().getNodeOffset(),
                                cxxFileInfo);
                cxxFileInfo.addReference(token);
            }
        }

        /**
         * ????????????
         *
         * @author z00484120
         * @since 3.0.0
         */
        public class VariableInfo {
            // ??????????????????
            String className;
            // ????????????namespace
            String namespace;

            // ????????????????????????
            int startLineNumber;

            // ??????????????????offset
            int startOffset;

            public VariableInfo(String className, String namespace, int startLineNumber, int startOffset) {
                this.className = className;
                this.namespace = namespace;
                this.startLineNumber = startLineNumber;
                this.startOffset = startOffset;
            }
        }
    }
}
