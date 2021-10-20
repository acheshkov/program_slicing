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
 *  使用cdt解析C/C++文件，获取文件中的定义和引用Token
 *
 * @author wutianyong (w00429929)
 * @version 1.0
 * @since 2019年3月26日
 */
public class CxxFileDefAndRefParser {
    // logger
    private static final Logger logger = LoggerFactory.getLogger(CxxFileDefAndRefParser.class);

    /**
     * CxxFileInfo
     */
    public CxxFileInfo cxxFileInfo;

    // 文件路径
    String filePath;

    public CxxFileDefAndRefParser() {}

    public CxxFileDefAndRefParser(String filePath) {
        this.filePath = filePath;
        cxxFileInfo = new CxxFileInfo(isHeaderFile(filePath));
    }

    /**
     * parseCustomizedFunctionDefinition
     *
     * @param functionDefinition 代码文件绝对路径
     * @param className 类名
     * @param namespace 所属的namespace
     * @param cxxFileInfo cxxFileInfo信息
     * @return void
     */
    public void parseCustomizedFunctionDefinition(
            CPPASTFunctionDefinition functionDefinition, String className, String namespace, CxxFileInfo cxxFileInfo) {}

    /**
     * 解析节点
     *
     * @param node 节点
     * param isReference
     * @return void
     */
    public void parseCustomizedProblemASTNode(IASTNode node, boolean isReference) {}

    /**
     * 解析代码文件，提取定义和引用的Token
     *
     * @param filePath 代码文件绝对路径
     * @return CodeFileInfo
     */
    public CxxFileInfo generateCodeFileInfo(String filePath) {
        // 计算文件名，文件夹，文件绝对路径
        String[] fileNameAndFolder = FileUtils.getFileNameAndDirectory(filePath);
        cxxFileInfo.fileName = fileNameAndFolder[0];
        cxxFileInfo.fileFolder = fileNameAndFolder[1];
        cxxFileInfo.filePath = Paths.get(cxxFileInfo.fileFolder, cxxFileInfo.fileName).normalize().toString();
        cxxFileInfo.offsetMap = calOffsetMap(filePath);

        // 解析代码文件，提取定义和引用的Token
        try {
            // 使用cdt解析文件获得TranslationUnit
            IASTTranslationUnit translationUnit = getTranslationUnit(filePath);

            // 解析include语句，提取头文件引用信息
            parseIncludeStatements(translationUnit);

            // 解析宏定义语句
            parseMacroDefinitons(translationUnit);

            // 解析声明/定义语句, 提取类、结构体、枚举、联合体，函数、全局变量信息
            parseDeclaration(translationUnit);
        } catch (Exception e) {
            // 解析失败
            cxxFileInfo.parseFailed = true;
            logger.error(ExceptionUtils.getStackTrace(e));
        } catch (Error e) {
            // 解析失败
            cxxFileInfo.parseFailed = true;
            cxxFileInfo.parseFailed = true;
            logger.error(ExceptionUtils.getStackTrace(e));
        }

        return cxxFileInfo;
    }

    /**
     * 调用cdt解析文件，获取TranslationUnit
     *
     * @param filePath 文件路径
     * @return TranslationUnit
     * @throws Exception
     */
    public IASTTranslationUnit getTranslationUnit(String filePath) throws Exception {
        PreprocessedFile processedFile = CxxCodeAnalyzer.preprocess(filePath, true);
        IASTTranslationUnit translationUnit = CxxCodeAnalyzer.getTranslationUnit(processedFile);
        return translationUnit;
    }

    /**
     * 解析include语句，提取头文件引用信息
     *
     * @param translationUnit 编译单元
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
     * 解析宏语句，提取定义和引用Token，加入代码文件信息中
     *
     * @param translationUnit TranslationUnit
     */
    public void parseMacroDefinitons(IASTTranslationUnit translationUnit) {
        // 获取文件中所有宏语句
        IASTPreprocessorMacroDefinition[] macroDefinitions = translationUnit.getMacroDefinitions();

        // 遍历
        for (IASTPreprocessorMacroDefinition macroDefinition : macroDefinitions) {
            // 获取宏的源Token和目标Token名称

            String sourceName = macroDefinition.getExpansion();

            IASTName destNameNode = macroDefinition.getName();
            String destName = destNameNode.getRawSignature();

            // 源Token -> 引用Token
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

            // 目标Token -> 定义Token
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
     * 分析include语句，推断其所属文件夹信息
     *
     * @param statement statement
     * @return HeaderFileRef 头文件引用信息
     */
    private HeaderFileRef generateHeaderFileRef(IASTPreprocessorIncludeStatement statement) {
        HeaderFileRef headerFileRef = new HeaderFileRef();

        // 头文件引用的基本信息（原始字符串，所属文件，头文件名，相对路径
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
     * 格式化include语句中头文件的相对路径
     *
     * @param folder 文件夹路径
     * @return 格式化后的文件夹路径
     */
    private String formatRelativeFolder(String folder) {
        String fileSeperator = "/";
        if (folder.contains("\\")) {
            fileSeperator = "\\";
        }
        return folder.replace(".." + fileSeperator, "").replace("..", "");
    }

    /**
     * 解析声明/定义语句, 提取类、结构体、枚举、联合体，函数、全局变量信息
     *
     * @param translationUnit 编译单元
     *
     */
    private void parseDeclaration(IASTTranslationUnit translationUnit) {
        IASTDeclaration[] astDecs = translationUnit.getDeclarations();
        for (IASTDeclaration dec : astDecs) {
            parseDeclaration(dec, "", "");
        }
    }

    /**
     * 解析声明（定义）语句，提取定义和引用Token，加入代码文件信息中
     *
     * @param declaration 待解析的声明语句的AST节点
     * @param className 当前AST节点所属类名
     * @param namespace 当前AST节点所属namespace
     */
    public void parseDeclaration(IASTDeclaration declaration, String className, String namespace) {
        if (declaration instanceof CPPASTNamespaceDefinition) {
            // 该AST节点是namespace定义
            parseNamespaceDefinition((CPPASTNamespaceDefinition) declaration, namespace);
        } else if (declaration instanceof CPPASTSimpleDeclaration) {
            // 该AST节点是类/结构体/联合体/枚举/变量声明或定义
            parseSimpleDeclaration((CPPASTSimpleDeclaration) declaration, className, namespace);
        } else if (declaration instanceof CPPASTFunctionDefinition) {
            // 该AST节点是函数定义
            parseFunctionDefinition((CPPASTFunctionDefinition) declaration, className, namespace);
            parseCustomizedFunctionDefinition(
                    (CPPASTFunctionDefinition) declaration, className, namespace, cxxFileInfo);
        } else if (declaration instanceof CPPASTTemplateDeclaration) {
            // 该AST节点是Template定义
            parseTemplateDeclaration((CPPASTTemplateDeclaration) declaration, className, namespace);
        } else if (declaration instanceof CPPASTLinkageSpecification) {
            // 该AST节点是extern "C"声明
            CPPASTLinkageSpecification ls = (CPPASTLinkageSpecification) declaration;
            for (IASTDeclaration subDeclaration : ls.getDeclarations()) {
                parseDeclaration(subDeclaration, className, namespace);
            }
        } else {
            if (declaration instanceof CPPASTProblemDeclaration) {
                // 解析失败，直接遍历Token
                CPPASTProblemDeclaration problemDeclaration = (CPPASTProblemDeclaration) declaration;
                for (IASTNode node : problemDeclaration.getChildren()) {
                    parseProblemASTNode(node, true);
                }
            }
        }
    }

    /**
     * 解析namespace定义语句，提取定义和引用Token，加入代码文件信息中
     *
     * @param namespaceDefinition namespace定义AST节点
     * @param namespace 当前AST节点所属namespace，多个namespace间使用.分隔
     */
    private void parseNamespaceDefinition(CPPASTNamespaceDefinition namespaceDefinition, String namespace) {
        // 更新namespace
        String currentNamespaceName = namespaceDefinition.getName().toString();
        String fullNamesapceName = currentNamespaceName;
        if (!namespace.equals("")) {
            fullNamesapceName = namespace + "." + currentNamespaceName;
        }
        if (currentNamespaceName.equals("")) {
            fullNamesapceName = namespace;
        }

        // 遍历子声明语句
        IASTDeclaration[] declarations = namespaceDefinition.getDeclarations();
        for (IASTDeclaration subDeclaration : declarations) {
            parseDeclaration(subDeclaration, "", fullNamesapceName);
        }
    }

    /**
     * 解析简单声明语句，提取定义和引用Token，加入代码文件信息中
     *
     * @param simpleDeclaration 简单声明语句AST节点
     * @param className 当前AST节点所属类名
     * @param namespace 当前AST节点所属namespace
     */
    private void parseSimpleDeclaration(CPPASTSimpleDeclaration simpleDeclaration, String className, String namespace) {
        CPPASTCompositeTypeSpecifier typeSpecifier = isClassDeclaration(simpleDeclaration);
        if (typeSpecifier != null) {
            // 该节点是类/结构体/联合体定义语句
            parseClassDeclaration(simpleDeclaration, typeSpecifier, namespace);
        } else if (simpleDeclaration.getDeclSpecifier() instanceof CPPASTEnumerationSpecifier) {
            // 该节点是枚举定义语句
            parseEnumDeclaration(simpleDeclaration, className, namespace);
        } else {
            // 该节点是typedef/变量声明/函数声明语句

            // 获取类型（变量类型、函数返回值类型等）
            String type = "";
            if (simpleDeclaration.getDeclSpecifier() != null) {
                type = simpleDeclaration.getDeclSpecifier().getRawSignature();
            }
            type = formatType(type);

            // 类的前向声明
            String patternStr = "class[ \t]";
            Pattern pattern = Pattern.compile(patternStr);
            Matcher matcher = pattern.matcher(type);
            if (matcher.find()) {
                type = type.replaceFirst("class", "").trim();
                // 增加一个新的前向声明Token
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

            // 遍历子声明体
            for (IASTDeclarator declarator : simpleDeclaration.getDeclarators()) {
                if (declarator instanceof CPPASTFunctionDeclarator) {
                    // 函数声明
                    parseFunctionDeclarator((CPPASTFunctionDeclarator) declarator, type, className, namespace, true);
                } else if (type.startsWith("typedef")) {
                    // typedef
                    parseTypedefDeclarator(simpleDeclaration, declarator, className, namespace);
                } else {
                    // 变量声明
                    parseFieldDeclarator(declarator, type, className, namespace);
                }
            }
        }
    }

    /**
     * 解析类声明语句，提取定义和引用Token，加入代码文件信息中
     *
     * @param simpleDeclaration 简单声明语句AST节点
     * @param typeSpecifier 类名标识
     * @param namespace 当前AST节点所属namespace
     */
    private void parseClassDeclaration(
            CPPASTSimpleDeclaration simpleDeclaration, CPPASTCompositeTypeSpecifier typeSpecifier, String namespace) {
        // 获取类名
        String className = typeSpecifier.getName().toString();
        if (!className.isEmpty()) {
            // 增加一个新的定义Token
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

        // 解析继承的父类
        if (typeSpecifier.getBaseSpecifiers() != null && typeSpecifier.getBaseSpecifiers().length > 0) {
            for (int i = 0; i < typeSpecifier.getBaseSpecifiers().length; i++) {
                ICPPASTBaseSpecifier baseSpec = typeSpecifier.getBaseSpecifiers()[i];
                // 获取父类完整名称
                String fullParentName = baseSpec.getNameSpecifier().getRawSignature().replace("::", ".");

                // 获取父类namespace和类名
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

                // 增加一个新的引用Token
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
            // 遍历成员变量和成员函数节点
            for (IASTDeclaration member : typeSpecifier.getMembers()) {
                parseDeclaration(member, className, namespace);
            }
        }

        // 如果是一个typedef语句
        if (simpleDeclaration.getRawSignature().startsWith("typedef")) {
            // 获取typedef的目标类型
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

            // 重新遍历成员变量和成员函数
            for (IASTDeclaration member : typeSpecifier.getMembers()) {
                parseDeclaration(member, destName, namespace);
            }
        }
    }

    /**
     * 解析枚举类型声明语句，提取定义和引用Token，加入代码文件信息中
     *
     * @param simpleDeclaration 简单声明语句AST节点
     * @param className 当前AST节点所属类名
     * @param inputNameSpace 当前AST节点所属namespace
     */
    private void parseEnumDeclaration(CPPASTSimpleDeclaration simpleDeclaration,
        String className, String inputNameSpace) {
        String namespace = inputNameSpace;
        // 计算namespace
        if (!className.equals("")) {
            if (namespace.equals("")) {
                namespace = className;
            } else {
                namespace += "." + className;
            }
        }

        // 计算类名
        CPPASTEnumerationSpecifier enumerationSpecifier =
                (CPPASTEnumerationSpecifier) simpleDeclaration.getDeclSpecifier();
        String enumClassName = enumerationSpecifier.getName().toString();

        // 增加一个新的定义Token
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

        // 遍历成员变量声明
        for (IASTDeclarator declarator : simpleDeclaration.getDeclarators()) {
            parseFieldDeclarator(declarator, enumClassName, className, namespace);
        }

        // 遍历枚举常量声明
        for (IASTEnumerator enumerator : enumerationSpecifier.getEnumerators()) {
            // 增加一个新的定义Token
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

        // 如果是一个typedef语句
        if (simpleDeclaration.getRawSignature().startsWith("typedef")) {
            // 获取typedef的目标类型
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

            // 遍历成员变量声明
            for (IASTDeclarator declarator : simpleDeclaration.getDeclarators()) {
                parseFieldDeclarator(declarator, enumClassName, className, namespace);
            }

            // 遍历枚举常量声明
            for (IASTEnumerator enumerator : enumerationSpecifier.getEnumerators()) {
                // 增加一个新的定义Token
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
     * 解析函数定义语句，提取定义和引用Token，加入代码文件信息中
     *
     * @param functionDefinition 函数定义语句AST节点
     * @param className 当前AST节点所属类名
     * @param namespace 当前AST节点所属namespace
     */
    private void parseFunctionDefinition(
            CPPASTFunctionDefinition functionDefinition, String className, String namespace) {
        // 解析函数返回值类型
        IASTDeclSpecifier declSpecifier = functionDefinition.getDeclSpecifier();
        String type = "";
        if (declSpecifier != null) {
            type = declSpecifier.getRawSignature();
        }
        type = formatType(type);

        // 解析函数声明节点
        parseFunctionDeclarator(
                (CPPASTFunctionDeclarator) functionDefinition.getDeclarator(), type, className, namespace, false);

        // 解析函数体
        parseFunctionBody(functionDefinition.getBody());
    }

    /**
     * 解析函数声明语句，提取定义和引用Token，加入代码文件信息中
     *
     * @param functionDeclarator 函数声明语句AST节点
     * @param inputClassName 当前AST节点所属类名
     * @param namespace 当前AST节点所属namespace
     * @param isFunctionDeclaration 是否为函数声明
     */
    private void parseFunctionDeclarator(
            CPPASTFunctionDeclarator functionDeclarator,
            String inputType,
            String inputClassName,
            String namespace,
            boolean isFunctionDeclaration) {
        String className = inputClassName;
        // 获取函数名
        String functionName = functionDeclarator.getName().getLastName().toString();
        if (functionName.equals("")) {
            IASTDeclarator declarator = functionDeclarator.getNestedDeclarator();
            if (declarator != null) {
                functionName = declarator.getName().getRawSignature();
            }
        }

        // 获取函数所属类名
        if (className.equals("")) {
            String fullFunctionName = functionDeclarator.getName().toString();
            int index = fullFunctionName.lastIndexOf("::");
            if (index > 0) {
                className = fullFunctionName.substring(0, index);
            }
        }

        // 增加一个新的定义Token
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

        // 返回值类型，增加一个新的引用Token
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

        // 解析函数参数
        for (ICPPASTParameterDeclaration parameterDeclaration : functionDeclarator.getParameters()) {
            // 获取函数参数类型
            String paramType = formatType(getParameterType(parameterDeclaration));
            // 增加一个新的引用Token
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
     * 解析函数体，提取定义和引用Token，加入代码文件信息中
     *
     * @param body 函数体的AST节点
     */
    private void parseFunctionBody(IASTStatement body) {
        if (body != null) {
            body.accept(new FunctionBodyVisitor(cxxFileInfo));
        }
    }

    /**
     * 解析变量声明语句，提取定义和引用Token，加入代码文件信息中
     *
     * @param declarator 变量声明的AST节点
     * @param type 变量类型
     * @param className 当前AST节点所属类名
     * @param namespace 当前AST节点所属namespace
     */
    private void parseFieldDeclarator(IASTDeclarator declarator, String type, String className, String namespace) {
        // 获取变量名
        String varName = declarator.getName().toString();

        if (varName.isEmpty()) {
            // 变量名为空的话，可能是一个函数式宏的引用
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
            // 解析剩余token
            parseProblemASTNode(declarator, true);
        } else {
            // 增加一个定义Token
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

        // 解析初始化语句
        IASTInitializer initializer = declarator.getInitializer();
        if (initializer != null) {
            initializer.accept(new FunctionBodyVisitor(cxxFileInfo));
        }
    }

    /**
     * 解析typedef语句，提取定义和引用Token，加入代码文件信息中
     *
     * @param simpleDeclaration 简单声明语句AST节点
     * @param declarator 声明体节点
     * @param className 当前AST节点所属类名
     * @param namespace 当前AST节点所属namespace
     */
    private void parseTypedefDeclarator(
            CPPASTSimpleDeclaration simpleDeclaration, IASTDeclarator declarator, String className, String namespace) {
        // 获取typedef源类型
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

        // 解析typedef目标类型，可能是一个函数指针
        parseProblemASTNode(declarator, false);
    }

    /**
     * 解析template语句，提取定义和引用Token，加入代码文件信息中
     *
     * @param templateDeclaration template语句AST节点
     * @param className 当前AST节点所属类名
     * @param namespace 当前AST节点所属namespace
     */
    private void parseTemplateDeclaration(
            CPPASTTemplateDeclaration templateDeclaration, String className, String namespace) {}

    /**
     * 解析错误的语句，提取定义和引用Token，加入代码文件信息中
     *
     * @param node AST节点
     *            代码文件信息
     * @param isReference  是否为引用token
     */
    public void parseProblemASTNode(IASTNode node, boolean isReference) {
        try {
            int startOffset = node.getNodeLocations()[0].getNodeOffset();
            IToken token = node.getSyntax();
            while (token != null) {
                // 跳过非identifier的token
                if (token.getType() != IToken.tIDENTIFIER) {
                    token = token.getNext();
                    continue;
                }

                // 获取token名
                String tokenStr = new String(token.getCharImage());
                int tokenStartOffset = startOffset + token.getOffset();
                int startLineNum = cxxFileInfo.getStartLineNumberByOffset(tokenStartOffset);

                // 新建Token
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
     * 判断AST节点是否为类（结构体/联合体）声明节点
     *
     * @param simpleDeclaration 简单声明语句AST节点
     * @return CPPASTCompositeTypeSpecifier，如果不是类声明节点，则返回null
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
     * 获取函数参数类型
     *
     * @param parameterDeclaration 函数参数声明AST节点
     * @return 函数参数类型
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
     * 解析一个类型字符串，获取类和namespace
     *
     * @param type 类型字符串
     * @return {类名, namespace}
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
     * 格式化类型字符串，去除修饰符
     *
     * @param type 类型字符串
     * @return 格式化后的类型
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
     * 判断一个文件是否为头文件
     *
     * @param filePath 文件路径
     * @return 是头文件true，不是头文件false
     */
    private boolean isHeaderFile(String filePath) {
        return FileUtils.isValidExtension(filePath, Constant.HEADER_FILE_EXTENSION);
    }

    /**
     * 计算offset和行号的对应关系
     *
     * @param filePath 文件路径
     * @return offset和行号的对应关系
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
     * 函数体遍历类
     *
     * @author z00484120
     * @since 3.0.0
     */
    public class FunctionBodyVisitor extends ASTVisitor {
        // 代码文件信息
        CxxFileInfo cxxFileInfo;

        // 变量类型栈，栈的每个元素保存当前scope下所有的变量与变量信息的映射
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
                // 变量声明语句
                CPPASTDeclarationStatement declarationStatement = (CPPASTDeclarationStatement) statement;
                if (declarationStatement.getDeclaration() instanceof CPPASTSimpleDeclaration) {
                    CPPASTSimpleDeclaration simpleDeclaration =
                            (CPPASTSimpleDeclaration) declarationStatement.getDeclaration();

                    // 获取变量类型
                    String type = "";
                    if (simpleDeclaration.getDeclSpecifier() != null) {
                        type = simpleDeclaration.getDeclSpecifier().getRawSignature();
                    }
                    type = formatType(type);
                    String[] classAndNamespace = getClassAndNamespace(type);

                    // 获取变量名
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
                    // 复合语句
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
         * 变量信息
         *
         * @author z00484120
         * @since 3.0.0
         */
        public class VariableInfo {
            // 变量所属类名
            String className;
            // 变量所属namespace
            String namespace;

            // 变量声明起始行号
            int startLineNumber;

            // 变量声明起始offset
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
