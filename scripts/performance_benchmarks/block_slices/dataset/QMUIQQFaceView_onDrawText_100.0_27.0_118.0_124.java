private void onDrawText(Canvas canvas, CharSequence text, float[] fontWidths, int offset, int widthStart, int widthEnd) {
        if (offset >= text.length()) {
            return;
        }
        if (mIsNeedEllipsize) {
            if (mEllipsize == TextUtils.TruncateAt.START) {
                if (mCurrentDrawLine > mLines - mNeedDrawLine) {
                    onRealDrawText(canvas, text, fontWidths, offset, widthStart, widthEnd);
                } else if (mCurrentDrawLine < mLines - mNeedDrawLine) {
                    for (int i = offset; i < text.length(); i++) {
                        if (mCurrentDrawUsedWidth + fontWidths[i] <= widthEnd) {
                            mCurrentDrawUsedWidth += fontWidths[i];
                        } else {
                            toNewDrawLine(widthStart, widthEnd - widthStart);
                            onDrawText(canvas, text, fontWidths, i, widthStart, widthEnd);
                            return;
                        }
                    }
                } else {
                    int needStopWidth = mCurrentCalWidth + mEllipsizeTextLength;
                    for (int i = offset; i < text.length(); i++) {
                        if (mCurrentDrawUsedWidth + fontWidths[i] <= needStopWidth) {
                            mCurrentDrawUsedWidth += fontWidths[i];
                        } else {
                            int newStart = i + 1;
                            if (mCurrentDrawUsedWidth > needStopWidth) {
                                newStart = i;
                            }
                            toNewDrawLine(widthStart + mEllipsizeTextLength, widthEnd - widthStart);
                            onDrawText(canvas, text, fontWidths, newStart, widthStart, widthEnd);
                            return;
                        }
                    }
                }
            } else if (mEllipsize == TextUtils.TruncateAt.MIDDLE) {
                int ellipsizeLine = getMiddleEllipsizeLine();
                if (mCurrentDrawLine < ellipsizeLine) {
                    int targetDrawWidth = mCurrentDrawUsedWidth;
                    for (int i = offset; i < fontWidths.length; i++) {
                        if (targetDrawWidth + fontWidths[i] <= widthEnd) {
                            targetDrawWidth += fontWidths[i];
                        } else {
                            drawText(canvas, text, offset, i, widthEnd - mCurrentDrawUsedWidth);
                            toNewDrawLine(widthStart, widthEnd - widthStart);
                            onDrawText(canvas, text, fontWidths, i, widthStart, widthEnd);
                            return;
                        }
                    }
                    drawText(canvas, text, offset, text.length(), targetDrawWidth - mCurrentDrawUsedWidth);
                    mCurrentDrawUsedWidth = targetDrawWidth;
                } else if (mCurrentDrawLine == ellipsizeLine) {
                    if (mIsExecutedMiddleEllipsize) {
                        handleTextAfterMiddleEllipsize(canvas, text, fontWidths, offset,
                                ellipsizeLine, widthStart, widthEnd);
                    } else {
                        int needStop = (widthEnd + widthStart) / 2 - mEllipsizeTextLength / 2;
                        int targetDrawWidth = mCurrentDrawUsedWidth;
                        for (int i = offset; i < fontWidths.length; i++) {
                            if (targetDrawWidth + fontWidths[i] <= needStop) {
                                targetDrawWidth += fontWidths[i];
                            } else {
                                drawText(canvas, text, offset, i, targetDrawWidth - mCurrentDrawUsedWidth);
                                mCurrentDrawUsedWidth = targetDrawWidth;
                                drawText(canvas, mEllipsizeText, 0, mEllipsizeText.length(), mEllipsizeTextLength);
                                mMiddleEllipsizeWidthRecord = mCurrentDrawUsedWidth + mEllipsizeTextLength;
                                mIsExecutedMiddleEllipsize = true;
                                handleTextAfterMiddleEllipsize(canvas, text, fontWidths, i,
                                        ellipsizeLine, widthStart, widthEnd);
                                return;
                            }
                        }
                        drawText(canvas, text, offset, text.length(), targetDrawWidth - mCurrentDrawUsedWidth);
                        mCurrentDrawUsedWidth = targetDrawWidth;
                    }
                } else {
                    handleTextAfterMiddleEllipsize(canvas, text, fontWidths, offset,
                            ellipsizeLine, widthStart, widthEnd);
                }
            } else {
                if (mCurrentDrawLine < mNeedDrawLine) {
                    int targetUsedWidth = mCurrentDrawUsedWidth;
                    for (int i = offset; i < fontWidths.length; i++) {
                        if (targetUsedWidth + fontWidths[i] <= widthEnd) {
                            targetUsedWidth += fontWidths[i];
                        } else {
                            drawText(canvas, text, offset, i, widthEnd - mCurrentDrawUsedWidth);
                            toNewDrawLine(widthStart, widthEnd - widthStart);
                            onDrawText(canvas, text, fontWidths, i, widthStart, widthEnd);
                            return;
                        }
                    }
                    drawText(canvas, text, offset, fontWidths.length, targetUsedWidth - mCurrentDrawUsedWidth);
                    mCurrentDrawUsedWidth = targetUsedWidth;
                } else if (mCurrentDrawLine == mNeedDrawLine) {
                    int ellipsizeLength = mMoreActionTextLength;
                    if (mEllipsize == TextUtils.TruncateAt.END) {
                        ellipsizeLength += mEllipsizeTextLength;
                    }

                    int targetUsedWidth = mCurrentDrawUsedWidth;
                    for (int i = offset; i < fontWidths.length; i++) {
                        if (targetUsedWidth + fontWidths[i] <= widthEnd - ellipsizeLength) {
                            targetUsedWidth += fontWidths[i];
                        } else {
                            drawText(canvas, text, offset, i, targetUsedWidth - mCurrentDrawUsedWidth);
                            mCurrentDrawUsedWidth = targetUsedWidth;
                            if (mEllipsize == TextUtils.TruncateAt.END) {
                                drawText(canvas, mEllipsizeText, 0, mEllipsizeText.length(), mEllipsizeTextLength);
                                mCurrentDrawUsedWidth += mEllipsizeTextLength;
                            }
                            drawMoreActionText(canvas, widthEnd);
                            // 依然要去到下一行，使得后续不会进入这个逻辑
                            toNewDrawLine(widthStart, widthEnd - widthStart);
                            return;
                        }
                    }
                    drawText(canvas, text, offset, fontWidths.length, targetUsedWidth - mCurrentDrawUsedWidth);
                    mCurrentDrawUsedWidth = targetUsedWidth;
                }
            }

        } else {
            onRealDrawText(canvas, text, fontWidths, 0, widthStart, widthEnd);
        }
    }