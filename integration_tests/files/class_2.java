/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
 */

package com.huawei.codebot.analyzer.cxx.kernel;

import com.huawei.codebot.analyzer.cxx.CxxGenericDefectFixer;
import com.huawei.codebot.analyzer.cxx.DefectFixerType4C;
import com.huawei.codebot.codeparsing.cxx.CxxFileModel;
import com.huawei.codebot.framework.FixerInfo;
import com.huawei.codebot.framework.exception.CodeBotRuntimeException;
import com.huawei.codebot.framework.model.DefectInstance;

import org.eclipse.cdt.core.dom.ast.ASTVisitor;
import org.eclipse.cdt.core.dom.ast.IASTStatement;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * 功能描述 kernel规范32:打印数字时不要使用小括号，如：\"(%d)\"
 *
 * @author m00365463 g00413998
 * @since 2020-07-02
 */
public class NumPrintUseBracketVisitor extends CxxGenericDefectFixer {
    private static final Logger logger = LoggerFactory.getLogger(NumPrintUseBracketVisitor.class);

    private static String PRINT_PATTERN = "\\w*\\s*\\(\\s*\".*\"[\\s\\S]*\\).*";

    private Set<Integer> errorLines = new HashSet<>();

    private void create(CxxFileModel fileModel) {
        fileModel.getAstTranlationUnit().accept(new ASTVisitor() {
            {
                shouldVisitStatements = true;
            }

            @Override
            public int visit(IASTStatement statement) {
                check(statement);
                return ASTVisitor.PROCESS_CONTINUE;
            }
        });
    }

    private void saveViolationItem(Integer line) {
        if (!errorLines.contains(line)) {
            errorLines.add(line);
            String defectMsg = this.getFixerInfo().getDescription();
            saveDefectInstance(line, defectMsg);

        }
    }

    private boolean numPrintUseBracket(String sourceCode) {
        String sourceTemp = sourceCode;
        while (sourceTemp.contains("%d")) {
            int endIndex = sourceTemp.indexOf("%d");
            int i = 0;
            for (i = endIndex - 1; i >= 0; i--) {
                if (Character.isWhitespace(sourceTemp.charAt(i))) {
                    continue;
                }
                if (sourceTemp.charAt(i) == '(' || sourceTemp.charAt(i) == '（') {
                    return true;
                } else {
                    break;
                }
            }
            sourceTemp = sourceTemp.substring(endIndex + 2);
        }
        return false;
    }

    private void check(IASTStatement statement) {
        String sourceCode = statement.getRawSignature();
        if (sourceCode.matches(PRINT_PATTERN)) {
            boolean violateFlag = numPrintUseBracket(sourceCode);
            if (violateFlag) {
                saveViolationItem(statement.getFileLocation().getStartingLineNumber());
            }
        }
    }

    @Override
    public List<DefectInstance> detectDefectsForFileModel(CxxFileModel fileModel) throws CodeBotRuntimeException {
        create(fileModel);
        return this.getCurrentFileDefectInstances();
    }

    @Override
    public FixerInfo getFixerInfo() {
        if (this.fixerInfo == null) {
            FixerInfo info = new FixerInfo();
            info.type = DefectFixerType4C.C_RULE_ID_PRINT_NUMBER_DONT_USE_BRACKET;
            info.description = "kernel规范32:打印数字时不要使用小括号，如：\"(%d)\"";
            this.fixerInfo = info;
        }
        return this.fixerInfo;
    }
}
