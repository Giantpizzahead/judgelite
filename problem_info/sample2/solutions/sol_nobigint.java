import java.util.*;
import java.io.*;

public class sol_nobigint {
    public static void main(String[] args) throws IOException {
        BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(in.readLine());

        boolean first = true;
        while (st.hasMoreTokens()) {
            if (!first) System.out.print(' ');
            first = false;

            String str = st.nextToken();
            try {
                long x = Long.parseLong(str);
                System.out.print(x * 2);
            } catch (NumberFormatException e) {
                System.out.print(str);
            }
        }
        // Missing newline print at end, but the grader will still accept the output
        // System.out.println();
    }
}