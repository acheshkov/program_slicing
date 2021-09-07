@SuppressWarnings("unchecked")
		private IterativeCondition<T> getIgnoreCondition(Pattern<T, ?> pattern) {
			Quantifier.ConsumingStrategy consumingStrategy = pattern.getQuantifier().getConsumingStrategy();
			if (headOfGroup(pattern)) {
				// for the head pattern of a group pattern, we should consider the inner consume strategy
				// of the group pattern if the group pattern is not the head of the TIMES/LOOPING quantifier;
				// otherwise, we should consider the consume strategy of the group pattern
				if (isCurrentGroupPatternFirstOfLoop()) {
					consumingStrategy = currentGroupPattern.getQuantifier().getConsumingStrategy();
				} else {
					consumingStrategy = currentGroupPattern.getQuantifier().getInnerConsumingStrategy();
				}
			}

			IterativeCondition<T> ignoreCondition = null;
			switch (consumingStrategy) {
				case STRICT:
					ignoreCondition = null;
					break;
				case SKIP_TILL_NEXT:
					ignoreCondition = new RichNotCondition<>((IterativeCondition<T>) pattern.getCondition());
					break;
				case SKIP_TILL_ANY:
					ignoreCondition = BooleanConditions.trueFunction();
					break;
			}

			if (currentGroupPattern != null && currentGroupPattern.getUntilCondition() != null) {
				ignoreCondition = extendWithUntilCondition(
					ignoreCondition,
					(IterativeCondition<T>) currentGroupPattern.getUntilCondition(),
					false);
			}
			return ignoreCondition;
		}