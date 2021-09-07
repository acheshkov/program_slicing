static void examineVn(MapSTL<Long, OptimizeRecord> recs, VarnodeTpl vn, int i, int inslot,
			int secnum) {
		if (vn == null) {
			return;
		}
		if (!vn.getSpace().isUniqueSpace()) {
			return;
		}
		if (vn.getOffset().getType() != ConstTpl.const_type.real) {
			return;
		}

		IteratorSTL<Pair<Long, OptimizeRecord>> iter;
		iter = recs.find(vn.getOffset().getReal());
		if (iter.isEnd()) {
			recs.put(vn.getOffset().getReal(), new OptimizeRecord());
			iter = recs.find(vn.getOffset().getReal());
		}
		if (inslot >= 0) {
			iter.get().second.readop = i;
			iter.get().second.readcount += 1;
			iter.get().second.inslot = inslot;
			iter.get().second.readsection = secnum;
		}
		else {
			iter.get().second.writeop = i;
			iter.get().second.writecount += 1;
			iter.get().second.writesection = secnum;
		}
	}