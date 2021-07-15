public void computeConstant() {
	//a special constant is use for the potential Integer.MAX_VALUE+1
	//which is legal if used with a - as prefix....cool....
	//notice that Integer.MIN_VALUE  == -2147483648

	long MAX = Integer.MAX_VALUE;
	if (this == One) {	constant = IntConstant.fromValue(1); return ;}
	
	int length = source.length;
	long computedValue = 0L;
	if (source[0] == '0')
	{	MAX = 0xFFFFFFFFL ; //a long in order to be positive ! 	
		if (length == 1) {	constant = IntConstant.fromValue(0); return ;}
		final int shift,radix;
		int j ;
		if ( (source[1] == 'x') || (source[1] == 'X') )
		{	shift = 4 ; j = 2; radix = 16;}
		else
		{	shift = 3 ; j = 1; radix = 8;}
		while (source[j]=='0') 
		{	j++; //jump over redondant zero
			if (j == length)
			{	//watch for 000000000000000000
				constant = IntConstant.fromValue(value = (int)computedValue);
				return ;}}
		
		while (j<length)
		{	int digitValue ;
			if ((digitValue = ScannerHelper.digit(source[j++],radix))	< 0 ) 	
			{	constant = FORMAT_ERROR; return ;}
			computedValue = (computedValue<<shift) | digitValue ;
			if (computedValue > MAX) return /*constant stays null*/ ;}}
	else
	{	//-----------regular case : radix = 10-----------
		for (int i = 0 ; i < length;i++)
		{	int digitValue ;
			if ((digitValue = ScannerHelper.digit(source[i],10))	< 0 ) 
			{	constant = FORMAT_ERROR; return ;}
			computedValue = 10*computedValue + digitValue;
			if (computedValue > MAX) return /*constant stays null*/ ; }}

	constant = IntConstant.fromValue(value = (int)computedValue);
		
}