import java.util.*;

public class sol {
    /*
    This should barely MLE and TLE.
    */
    static void testBorder() {
        int SIZE = 16000000;
        int[] arr = new int[SIZE];
        for (int i = 0; i < SIZE; i++) {
            arr[i] = i + 3;
            for (int j = 1; j < 70; j++) {
                arr[i/j] += arr[i];
            }
        }
    }
    
    /*
    This should MLE.
    */
    static void testMLE() {
        int[] arr = new int[150000000];
    }
    
    /*
    This should TLE.
    */
    static void testTLE() {
        int sum = 0;
        for (int i = 0; i < 1000000000; i++) {
            sum += i;
            sum %= (i+2)/2;
        }   
    }
    
    /*
    This should RE.
    */
    static void testRE() {
        int[] arr = new int[8];
        arr[-2] = 9;
    }
    
    static int testStack(int i, int x) {
        if (i == 0) return 9;
        else return testStack(i-1, x * 2);
    }
    
    public static void main(String[] args) {
        // testBorder();
        // testMLE();
        // testTLE();
        // testRE();
        // testStack(50000, 13);
        
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();

        long sum = 0;
        for (int i = 0; i < N; i++) {
            sum += sc.nextInt();
        }

        System.out.print(sum);
    }
}
