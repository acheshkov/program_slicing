    public static String getFunctionName(AST ast) {
	assert isCast(ast);
	AST operator = AstUtil.findChildOfType(ast, CPPTokenTypes.LITERAL_OPERATOR);
	if( operator == null ) {
            // error in AST
	    return "operator ???"; // NOI18N
	}
	StringBuilder sb = new StringBuilder(operator.getText());
	sb.append(' ');
	begin:
	for( AST next = operator.getNextSibling(); next != null; next = next.getNextSibling() ) {
	    switch( next.getType() ) {
		case CPPTokenTypes.CSM_TYPE_BUILTIN:
		case CPPTokenTypes.CSM_TYPE_COMPOUND:
		    sb.append(' ');
		    addTypeText(next, sb);
                    break;
		case CPPTokenTypes.CSM_PTR_OPERATOR:
		    addTypeText(next, sb);
                    break;
		case CPPTokenTypes.LPAREN:
		    break begin;
		case CPPTokenTypes.AMPERSAND:
		case CPPTokenTypes.STAR:
		case CPPTokenTypes.LITERAL_const:
                case CPPTokenTypes.LITERAL___const:    
                case CPPTokenTypes.LITERAL___const__:
		    sb.append(next.getText());
		    break;
		default:
		    sb.append(' ');
		    sb.append(next.getText());
	    }
	}
	return sb.toString();
    }