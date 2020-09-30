import java.util.*;
import java.io.*;

public class checker {

    public static void main(String[] args) throws IOException {
        Scanner sc = new Scanner(System.in);
        int N = sc.nextInt();

        BufferedReader fin = new BufferedReader(new FileReader(args[1]));
        int M = Integer.parseInt(fin.readLine());

        if (N < 1 || N > 1000000000) System.out.println(0);
        else if (N % M != 0) System.out.println(0);
        else System.out.println(1);
    }
}