/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2019-2020. All rights reserved.
 */

package com.huawei.codebot.analyzer.cxx.astviewer.treeview.ast;

import org.eclipse.cdt.core.dom.ast.IASTCompoundStatement;
import org.eclipse.cdt.core.dom.ast.IASTName;
import org.eclipse.cdt.core.dom.ast.IASTNamedTypeSpecifier;
import org.eclipse.cdt.core.dom.ast.IASTNode;
import org.eclipse.cdt.core.dom.ast.IASTNodeLocation;
import org.eclipse.cdt.core.dom.ast.IASTSimpleDeclaration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.huawei.codebot.analyzer.cxx.astviewer.treeview.AbstractTreeTableModel;
import com.huawei.codebot.analyzer.cxx.astviewer.treeview.TreeTableModel;

/**
 * 功能描述
 *
 * @author j00404394
 * @since 2018-01-24
 */
public class ASTTreeModel extends AbstractTreeTableModel implements TreeTableModel {
    private static final Logger logger = LoggerFactory.getLogger(ASTTreeModel.class);

    private static String[] cNames = {"Node", "Name", "LineNo", "Offset/Position"};

    private static Class[] cTypes = {TreeTableModel.class, String.class, String.class, String.class};

    /**
     * @param root 根节点
     */
    public ASTTreeModel(IASTNode root) {
        super(new TASTNode(root));
    }

    /**
     * 获取子节点个数
     * 
     * @param node node
     * @return int
     */
    public int getChildCount(Object node) {
        Object[] children = getChildren((IASTNode) node);
        return children == null ? 0 : children.length;
    }

    /**
     * 获取子节点
     * 
     * @param node node
     * @param i index
     * @return Object
     */
    public Object getChild(Object node, int i) {
        return getChildren((IASTNode) node)[i];
    }

    /**
     * 判断叶子节点
     * 
     * @param node node
     * @return boolean
     */
    public boolean isLeaf(Object node) {
        IASTNode astnode = (IASTNode) node;
        IASTNode[] children = getChildren(astnode);
        return (children == null) || (children.length == 0);
    }

    /**
     * 获取子节点
     * 
     * @param node node
     * @return IASTNode[]
     */
    protected IASTNode[] getChildren(IASTNode node) {
        return node.getChildren();
    }

    /**
     * 得到column个数
     * 
     * @return int
     */
    public int getColumnCount() {
        return cNames.length;
    }

    /**
     * column name
     * 
     * @param column column
     * @return String
     */
    public String getColumnName(int column) {
        return cNames[column];
    }

    /**
     * @param column column
     * @return Class
     */
    public Class getColumnClass(int column) {
        return cTypes[column];
    }

    /**
     * @param node node
     * @param column column
     * @return Object
     */
    public Object getValueAt(Object node, int column) {
        TASTNode noderef = (TASTNode) node;

        try {
            switch (column) {
                case 0:
                    return "nada";
                case 1:
                    IASTNode original = noderef.getOriginalNode();

                    if ((original instanceof IASTSimpleDeclaration)) {
                        return original.getRawSignature();
                    }

                    if (((original instanceof IASTNamedTypeSpecifier)) || ((original instanceof IASTName))) {
                        return original.toString();
                    }

                    if ((original instanceof IASTCompoundStatement)) {
                        return "{";
                    }

                    return "[[" + original.getRawSignature() + "]]";
                case 2: {
                    IASTNodeLocation[] nodeLocations = noderef.getNodeLocations();
                    StringBuilder sb = new StringBuilder();
                    for (IASTNodeLocation iastNodeLocation : nodeLocations) {
                        sb.append(noderef.getFileLocation().getStartingLineNumber());
                        sb.append(",");
                    }

                    if (sb.length() > 0) {
                        sb.deleteCharAt(sb.length() - 1);
                    }
                    return sb.toString();
                }
                case 3: {
                    IASTNodeLocation[] nodeLocations = noderef.getNodeLocations();
                    StringBuilder sb = new StringBuilder();
                    for (IASTNodeLocation iastNodeLocation : nodeLocations) {
                        sb.append(iastNodeLocation.getNodeOffset() + ":" + iastNodeLocation.getNodeLength());
                        sb.append(",");
                    }

                    if (sb.length() > 0) {
                        sb.deleteCharAt(sb.length() - 1);
                    }
                    return sb.toString();
                }
            }
        } catch (SecurityException localSecurityException) {
            logger.error(localSecurityException.getMessage());
        }
        return null;
    }
}
