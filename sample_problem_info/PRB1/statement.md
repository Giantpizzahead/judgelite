One day, Blake comes to you and begs you to help him with his homework! He asks you to write a program that can sum two numbers together, and print out the result.

However, as you begin writing this program, you ask yourself: *Why is Blake asking me to do this? Can't he just use a calculator?*

After thinking for a while, you realize that Blake is just SUPER lazy, which also explains why he's doing the homework on the day that it's due. So, you decide to teach Blake a lesson for relying on you to bail him out. You'll write the program for Blake... but you're going to intentionally give him the wrong answers.

Specifically, you'll write a program that **sums two numbers together**. However, **the result you print will always be 2 greater than the actual sum**. For example, if the two numbers your program receives are $4$ and $3$, your program would output $9$ instead of $7$. With any luck, Blake won't check your program's answers, and once he gets all the answers wrong, he'll learn not to bug you for EVERY. SINGLE. ASSIGNMENT.

Blake is waiting for you... pull this thing off! :)
(Note: Never do this to someone in real life.)

#### INPUT FORMAT

Your program will receive two integers $A$ and $B$, separated by a single space. These are the integers that Blake wants to know the sum of.

#### OUTPUT FORMAT

Your program should output one integer. This integer should be exactly 2 more than the sum of the numbers that Blake gave you.
(In mathy terms, you should output the value of $A + B + 2$.)

#### CONSTRAINTS

The numbers that Blake gives your program will both be in the range $1...10{,}000$.
(In mathy terms, $1 \leq A, B \leq 10{,}000$.)

#### SAMPLE INPUT
```text
9 10
```

#### SAMPLE OUTPUT
```text
21
```

#### EXPLANATION

$9 + 10 = 19$. Since your program should output $2$ more than the actual sum of the numbers, your program should output $21$.

Not sure which programming language to use? If you have prior experience with a programming language, that's the one you should use! Otherwise, Java would probably be your best bet, since the school's programming courses (Intro to Java / APCS) use Java.

If you need help, try getting a hint by clicking the hint button below! There's no penalty for using hints, but try your best to solve the problem without hints first.

#### HINTS

1. Here are some helpful links to learn how to parse input.
[Java Input Parsing](https://www.programiz.com/java-programming/scanner)
[C++ Input Parsing](https://www.learncpp.com/cpp-tutorial/introduction-to-iostream-cout-cin-and-endl/)
[Python 3 Input Parsing](https://pynative.com/python-input-function-get-user-input/)
Remember not to print any prompts like "Enter a number" or "The answer is" in your program. The grader will get confused by these prompts, and your solution may be marked as wrong! If you don't have much experience with the programming language you chose, it might help to learn the basics of that programming language before trying these challenge problems (variables, if/else statements, for loops, input/output).

2. Here is some sample source code for all 3 languages. However, all the programs below print out the *actual* sum of the two numbers, instead of printing out the number that is $2$ greater than the sum. Do you know how to fix it?

Java (You'll need to change the class name to match your file name)
```java
import java.util.Scanner;

public class PRB1 {
	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);
		int A = sc.nextInt();
		int B = sc.nextInt();
		int fakeSum = A + B;
		System.out.println(fakeSum);
	}
}
```
C++
```cpp
#include <iostream>

int main() {
	int A, B;
	std::cin >> A >> B;
	int fakeSum = A + B;
	std::cout << fakeSum << std::endl;
}
```
Python 3
```python
A, B = map(int, input().split())
fake_sum = A + B
print(fake_sum)
```