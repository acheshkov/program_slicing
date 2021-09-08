private int runTransaction(CaretTransaction.RemoveType removeType, int offset, CaretItem[] addCarets, CaretMoveHandler moveHandler) {
        return runTransaction(removeType, offset, addCarets, moveHandler, MoveCaretsOrigin.DEFAULT);
    }