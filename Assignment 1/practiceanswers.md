## HW 4 Query and Indexing

Submit your answers in the text file answers.txt. Please put your answer right after the question. If you want to put down how you got to your answer, put it on the line following lines. You can have just the answer,
but there is no chance for partial credit. Assume worst case for all lookups.
If there are multiple ways to look up the data (i.e. multiple indexes, index vs scan), use the cheapest method.

For example, imagine question 0 is ```How long (ms) to read two sequential pages```, your answers.txt would have something like

```
0) 11ms
9+2(1) for one seek and two reads
```

You will need to calculate the B+Tree fanout/degree, by calculating the max number of index entries as m for a B+page:
`page_size >= (m-1) * size(search key) + m * size(pointer)`

Imagine we have a page size of 1kb, with a search key size of 40 bytes and a pointer size of 10, we would have:
`1000 >= (m-1)*40+m*10`
`1040/50>= m`
`20.8>= m`
Since m must be an integer and we would like to hold the largest valid value for m, we therefor know that each page could hold at most 20 pointers and 19 keys.
(e.g  `20*10+19*40<=1000`)

For the following problems you will assume the following
information:

- Page sizes are 4kb (4000 bytes)
- 1mb = 1000kb
- Integers (int) are 4 bytes
- BigInts (big) are 8 bytes
- Characters (char) are 1 bytes
- Strings are fixed length char arrays of size n (str[n])
- Page pointers and pointers to a record ID are 8 bytes
- Assume data and index pages have 0 bytes for header data (magic). Assume
each page is filled up to be as full as possible, and that a record is never split across multiple pages.
- Each data record has 0 bytes for header and null/variable length data (magic)
- Assume each index entry is the search key + record id pointer. No additional metadata.
- Page seek cost is 9ms, page read time is 1ms
- No page is in memory. For questions 4-6 do not assume any page read will stay in memory.
- Hashtables are in memory (but the pages containing the index entries are on disk). Hashtables are static and perfectly sized (no overflow or chaining)
- Blocks = pages = B+Tree node size
- We have the schema `student` composed of :
  ```
  sname str(20)
  year int
  sid big
  major int
  ```

- We have the schema `course` composed of:
 ```
 cname str(40)
 cid int
 major int
 ```

- We have the schema `takes` composed of:
 ```
 cid int
 sid big
 grade int
 ```

- We have 12,000 students, 300 courses, and 34,000 takes records.
- The following indexes exist:
  - `student` has an unclustered hash index on sname, a clustered B+ tree index on sid, and an unclustered B+tree index on year
  - `course` has an unclustered B+tree index on cname and an unclustered B+tree index on major.
  - `takes` has an clustered B+tree index on sid
- For any join algorithm that uses nested-loop or hashing, you should make the smaller relation either the inner relation or the build relation.

## Questions

1) How big (in kb or mb) are the total data pages (e.g. student, course, + takes)
996 kb  = 436+16+544

Student Record Size = 20+4+8+4 = 36 bytes.
111 records per page (floor(4000/36) no split records).
ceil(12000/111)= 109 pages * 4kb = 436kb of Students

Course Record Size 40 + 4 + 4 = 48 bytes.
83 Course record/tuples per page (floor(4000/48)).
ceil(300/83) = 4 pages = 16kb of Course Data

Takes Record Size = 4 + 4 + 8 = 16 bytes
250 record per page (4000/16)
ceil(34000/250) = 136 pages = 544 kb of data

2a) What are the max index entries per page for sid index on takes?
249 index entries

key size = 8, pointer size =8

```
page_size >= (m-1) * size(search key) + m * size(pointer)
4000>= (m-1)*8 + m *8
4000 >= 16m-8
4008 >= 16m
250.5 >= m
```

m = 250 = number of pointers
250-1 = max number of keys
Can easily verify with 249*8 + 250*8  = 3992 (not enough for another pair of key and pointer)

2b) What are the min index entries per page for sid index on takes?
125

ceil(249/2)


3) How tall (root to leaf node) is the index (worst case) for the sid index on takes?
3

ceil(log_125(34000))

4) How long (ms) will it take to find a student's record by name?
10ms

One seek + one read/transfer

5) How long (ms) will it take to find all students whose year is 2020. Assume we have no more than 1,100 students with this year.

118 ms

Full table scan = 1 seek (9ms) + 109 page reads (at 1ms each) = 118 ms

Secondary B+Tree look up.
b+tree min pointers = 166
Height = ceil(log_166(12000)) = 2
Find all index entries = height + sequential pages for students =  `2*10+ floor(1100/111)*9` = 29ms to find index entries.  Assume random look ups for all 1100 students, 29ms+1100*10 = 11,029ms

```
key size = 4, pointer size =8
page_size >= (m-1) * size(search key) + m * size(pointer)
4000 >= (m-1)*4 + m *8
4000 >= 4m -4 + 8m
4000 >= 12m-4
4004 >= 12m
333.66 >= m
m = 333, max keys = 332
```

6) How long (ms) will it take to find all courses with major = 134. Assume there are no more than 50 courses per major.

13ms

Table scan: 9ms seek + 1ms * 4 = 13ms

B+Tree secondary look up is similar to problem 5, but we know 50 random lookups for the record looks up would dominate (or be the same as the scan plus the tree lookup)

7) If only 2 pages can be held in memory, how many pages (given in takes:X and courses:Y) will be read for a block nested loop join between takes and courses.

Smaller relation is courses (4), takes is 136 pages. Using worst case estimate = courses:136*4+takes:136 pages = (courses:544 + takes:136) =  680 pages

8) If 151 pages could be held in memory, what join algorithm would be best for joining takes and courses? How many pages (in terms of takes and courses) would this join algorithm read?

Block-nested loop can hold all pages in memory =  (takes:136+courses:4) = 140 pages

(hash join also works)

9) If we join student and takes what join algorithm would be best and how many pages would this join algorithm read (in terms of takes and students)? Assume each student does not take more than 20 courses and that 10 page could be held in memory.

Both are sorted by SID so merge-join would be cheapest. Back tracking would not evict any pages (enough memory). Read (students:109+takes:136 pages) = 245 pages
