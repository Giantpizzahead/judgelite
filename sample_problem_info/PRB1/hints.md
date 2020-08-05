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