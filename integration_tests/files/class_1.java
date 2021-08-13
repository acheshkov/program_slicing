/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2019-2020. All rights reserved.
 */

package com.huawei.codebot.analyzer.cxx.pclint;

import java.util.List;
import java.util.Locale;

import org.eclipse.cdt.core.dom.ast.ASTVisitor;
import org.eclipse.cdt.core.dom.ast.IASTDeclSpecifier;
import org.eclipse.cdt.core.dom.ast.IASTDeclaration;
import org.eclipse.cdt.core.dom.ast.IASTSimpleDeclaration;
import org.eclipse.cdt.core.dom.ast.IASTTranslationUnit;
import org.eclipse.cdt.core.dom.ast.cpp.ICPPASTCompositeTypeSpecifier;
import org.eclipse.cdt.core.dom.ast.cpp.ICPPASTSimpleDeclSpecifier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.huawei.codebot.analyzer.cxx.CxxGenericDefectFixer;
import com.huawei.codebot.analyzer.cxx.DefectFixerType4C;
import com.huawei.codebot.codeparsing.cxx.CxxFileModel;
import com.huawei.codebot.framework.FixerInfo;
import com.huawei.codebot.framework.exception.CodeBotRuntimeException;
import com.huawei.codebot.framework.model.DefectInstance;


/**
 * 功能描述 内联虚函数很不寻常，对应于PCLint 1558
 * 
 * @changed 2019-10-08 by bianpan 00536876 1. Associate with RuleID 201558 2. Change the warning information
 * @author 00406513
 * @since 2019-06-20
 */
public class InlineVirtualFunctionChecker extends CxxGenericDefectFixer {
    private static final Logger logger = LoggerFactory.getLogger(InlineVirtualFunctionChecker.class);

    private static final String VIRTUAL_FUNCTION = "InlineVirtualFunction";

    private static final Integer CHECK_RULE_ID = 0;


    private void check(IASTTranslationUnit translationUnit, String filePath) {
        logger.debug(String.format(Locale.ROOT, "Run %s checker on '%s'", VIRTUAL_FUNCTION, filePath));

        translationUnit.accept(new LocalVisitor());

        logger.debug(String.format(Locale.ROOT, "Completed %s checker on '%s'", VIRTUAL_FUNCTION, filePath));
    }

    @Override
    public List<DefectInstance> detectDefectsForFileModel(CxxFileModel fileModel) throws CodeBotRuntimeException {
        String filePath = fileModel.getFilePath();
        check(fileModel.getAstTranlationUnit(), filePath);
        return this.getCurrentFileDefectInstances();
    }

    @Override
    public FixerInfo getFixerInfo() {
        if (this.fixerInfo == null) {
            FixerInfo info = new FixerInfo();
            info.type = DefectFixerType4C.C_RULE_ID_INLINE_VIRTUAL_FUNCTION;
            info.description = "base specifier with no access specifier is implicitly public/private.";
            this.fixerInfo = info;
        }
        return this.fixerInfo;
    }

    private class LocalVisitor extends ASTVisitor {

        String mClassName = "";

        LocalVisitor() {
            this.shouldVisitDeclarations = true;
        }

        @Override
        public int visit(IASTDeclaration declaration) {
            if (declaration instanceof IASTSimpleDeclaration) {
                IASTSimpleDeclaration simpleDeclaration = (IASTSimpleDeclaration) declaration;
                IASTDeclSpecifier declSpecifier = simpleDeclaration.getDeclSpecifier();

                if (declSpecifier instanceof ICPPASTCompositeTypeSpecifier) {
                    ICPPASTCompositeTypeSpecifier compositeSpecifier = (ICPPASTCompositeTypeSpecifier) declSpecifier;

                    // New class found, record its name
                    mClassName = compositeSpecifier.getName().getRawSignature();
                    ;

                    for (IASTDeclaration memberDeclaration : compositeSpecifier.getMembers()) {
                        if (memberDeclaration instanceof IASTSimpleDeclaration) {
                            checkRule((IASTSimpleDeclaration) memberDeclaration);
                        }
                    }
                }
            }

            return PROCESS_CONTINUE;
        }

        private void checkRule(IASTSimpleDeclaration simpleDeclaration) {
            logger.debug(String.format(Locale.ROOT, "Checking method '%s'...", simpleDeclaration.getRawSignature()));
            IASTDeclSpecifier simpleSpecifier = simpleDeclaration.getDeclSpecifier();
            if (simpleSpecifier instanceof ICPPASTSimpleDeclSpecifier) {
                ICPPASTSimpleDeclSpecifier cppSpecifier = (ICPPASTSimpleDeclSpecifier) simpleSpecifier;
                boolean isVirtual = cppSpecifier.isVirtual();
                boolean isInline = cppSpecifier.isInline();
                if (isInline && isVirtual) {
                    int lineNumber = simpleDeclaration.getFileLocation().getStartingLineNumber();
                    String message = String.format(Locale.ROOT,
                        " Problem：class '%s' virtual function '%s' is declared as inline function", mClassName,
                        simpleDeclaration.getRawSignature());
                    saveDefectInstance(lineNumber, message);
                }
            }
        }
    }
}
