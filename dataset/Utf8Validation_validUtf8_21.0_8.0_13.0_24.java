public boolean validUtf8(int[] data) {
        int count = 0;

        for(int i : data) {
            if(count == 0) {
                if((i >> 5) == 0b110) {
                    count = 1;
                } else if((i >> 4) == 0b1110) {
                    count = 2;
                } else if((i >> 3) == 0b11110) {
                    count = 3;
                } else if((i >> 7) == 0b1) {
                    return false;
                }
            } else {
                if((i >> 6) != 0b10) {
                    return false;
                }

                count--;
            }
        }
        
        return count == 0;
    }