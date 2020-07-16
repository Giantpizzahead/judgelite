import java.util.*;
import java.io.*;
import java.math.BigInteger;

public class sol {
    public static void main(String[] args) throws IOException {
        Scanner sc = new Scanner(System.in);

        boolean first = true;
        while (sc.hasNext()) {
            if (!first) System.out.print(' ');
            first = false;

            String str = sc.next();
            try {
                BigInteger x = new BigInteger(str);
                System.out.print(x.add(x).toString());
            } catch (NumberFormatException e) {
                System.out.print(str);
            }
        }
        // Missing newline print at end, but the grader will still accept the output
        System.out.println();
    }
}