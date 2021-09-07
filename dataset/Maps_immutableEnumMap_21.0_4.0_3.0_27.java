@GwtCompatible(serializable = true)
  public static <K extends Enum<K>, V> ImmutableMap<K, V> immutableEnumMap(
      Map<K, ? extends V> map) {
    if (map instanceof ImmutableEnumMap) {
      @SuppressWarnings("unchecked") // safe covariant cast
      ImmutableEnumMap<K, V> result = (ImmutableEnumMap<K, V>) map;
      return result;
    }
    Iterator<? extends Entry<K, ? extends V>> entryItr = map.entrySet().iterator();
    if (!entryItr.hasNext()) {
      return ImmutableMap.of();
    }
    Entry<K, ? extends V> entry1 = entryItr.next();
    K key1 = entry1.getKey();
    V value1 = entry1.getValue();
    checkEntryNotNull(key1, value1);
    Class<K> clazz = key1.getDeclaringClass();
    EnumMap<K, V> enumMap = new EnumMap<>(clazz);
    enumMap.put(key1, value1);
    while (entryItr.hasNext()) {
      Entry<K, ? extends V> entry = entryItr.next();
      K key = entry.getKey();
      V value = entry.getValue();
      checkEntryNotNull(key, value);
      enumMap.put(key, value);
    }
    return ImmutableEnumMap.asImmutable(enumMap);
  }