[[00 (book) Cracking the Coding Interview]]

# Powers of 2 table 

![[power2.PNG]]

# Listen Carefully
 - at the beginning be sure to note down important details such as 
    
	«given 2 arrays that are ***sorted***» 
	
	or 
	
	«Design an algorithm to be run ***repeatedly*** on a server that ..»

 # Draw an example
 
 - make sure the example is not a special or best beautiful case scenario
  - make sure example is big enough and uses real world data/values in sufficient amounts (i.e. specific)

# State the brute force
- its not obvious to all the candidates so make sure inerviewer knows tha you know it
- state time and space complexity and move on to the optimizations

# Optimize

1. Look for any unused information. Did your interviewer tell you that the array was sorted? 
2. Use a fresh example. Sometimes, just seeing a different example will unclog your mind or help you see a pattern in the problem. 
3. Solve it"incorrectly:' Just like having an inefficient solution can help you find an efficient solution, having an incorrect solution might help you find a correct solution. For example, if you're asked to generate a random value from a set such that all values are equally likely, an incorrect solution might be one that returns a semi-random value: Any value could be returned, but some are more likely than others. You can then think about why that solution isn't perfectly random. Can you rebalance the probabilities? 
4. Make time vs. space tradeoff. Sometimes storing extra state about the problem can help you optimiz:e the runtime. 
5. Precompute information. Is there a way that you can reorganiz:e the data (sorting, etc.) or compute some values upfront that will help save time in the long run? 
6. Use a hash table. 
7. Think about the best conceivable runtime

# Walk through
- take a moment to understand the solution in more detail and make sure whiteboard code is correct and helps you get to coding faster with less hindrance

# Implement
- write beautiful modular code
- variable names that make sense
- handle errors or add comments such as TODO and explain to interviewer what your intentions later on are
- 
