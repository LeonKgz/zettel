[[00 (book) Cracking the Coding Interview]]

# Amortized Time

 - Amortized time complexity is the way to estimate the average time complexity of an operation overall even if it differs by case scenario. For example when inserting a value into an ArrayList usually it only takes O(1) time but once in a while we have to extend the array when we hit the limit and that takes O(n) time as we have to create a copy of the array double its size and copy all the existing elemnts into it. So we can mention the worst case scenario but say that the amortized time is O(1)
 
 # Log N time
 
 - whenever some problem is halved with each step in an algorithm it is like to have logN in it.

# Recursive complexity
in a function like this for example:
 
 	int f(int n) {
 		if (n <= 1) {
			return 1;
		}
		
		return f(n - 1) + f(n - 1);
	}
	
if we drew a tree we would see ![[rec_tree.PNG]]

So we can see the complexity is 2 to the power of n
In a general case it is the number of branches i.e. rrecursive function calls to the power of n (depth)

Here te number of branches matters since they differ by a magnitude of x^N unlike constant factors between log bases

The space complexity for this tree is O(n) as only O(n) nodes of the tree exist at any given time since when we are doing the recursive calls we can imagine traversing tree from one leaf to another in order (depth first of sorts) and thus complexity will be of O(depth) or O(n)

# Examples
- Example 8 — taking into acctoun size of strings when comparing them to each other as well 
- Example 9 — depth is log n actually and not n, so 2^logN = N so answer is O(N)
- Example 12 — n! leaves; depth of n therefore each of the leaves is attached to a path from the root to the leaf of depth n thus definitely no more than n * n! nodes all together. Each node also corresponds to O(n) work related to traversing the string (in either if else statements branches). so overall O(n^2 * n!)
- Example 13 Fibonacci function; we can simply state that the complexity is 2^n which would probably work in an interview setting. A more precise answer is 1.6^n 1.6 being the golden ratio phi (1 + root(5)) / 1, sollution to a^2 - a - 1 = 0; Answer is here https://stackoverflow.com/questions/360748/computational-complexity-of-fibonacci-sequence
- Example 14 — this is effectivly the sum of powers of two which is 2^(n+1) - 1 or O(2^n) still