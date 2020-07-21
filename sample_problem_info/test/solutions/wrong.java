import java.util.*;

public class wrong {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();

        if (N == 5) {
            int x = 3 / 0;
        }

        if (N == 2 || N == 8) {
            int SIZE = 300000000;
            int[] arr = new int[SIZE];
        }

        if (N == 3 || N == 10) {
            N--;
        }

        if (N == 6) {
            int x = 1;
            int y = 2;
            int z = 9;
            for (int i = 0; i < 2000000000; i++) {
                x = y + x;
                y = x * y;
                z = (x + y) * z;
                y += z * x;
            }
        }

        System.out.print(N);
    }
}
