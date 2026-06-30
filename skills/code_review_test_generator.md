# Code Review & Test Case Generator Skill

## Purpose

Use this skill to review code snippets, functions, classes, modules, or Git diffs and generate practical test cases.

The goal is to help developers improve code quality before merging or submitting code by identifying:

* Potential bugs
* Edge cases
* Exception handling issues
* Input validation gaps
* Security risks
* Maintainability problems
* Missing or weak test coverage

This skill should act like a careful senior backend engineer. Do not blindly trust the code or the AI-generated result. Always verify assumptions, check boundary conditions, and explain risks clearly.

---

## When to Use This Skill

Use this skill when the user asks for any of the following:

* Review this code
* Check this function
* Find bugs in this code
* Generate test cases
* Add unit tests
* Check edge cases
* Review this Git diff
* Help me improve this implementation
* Does this code have any risk?
* What tests should I write for this code?
* Use AI coding review for this change

Also use this skill when the user provides code and asks whether it is correct, safe, maintainable, or production-ready.

---

## Inputs

The user may provide:

1. A code snippet
2. A full function
3. A class or module
4. A Git diff
5. Error logs plus code
6. A short description of intended behavior
7. Existing tests
8. A target test framework, such as `pytest`, `JUnit`, `go test`, or `Jest`

If the user does not provide enough context, make reasonable assumptions, but clearly label them.

If critical information is missing, ask for clarification only when necessary. Otherwise, proceed with the review based on the available code.

---

## Supported Languages

Prioritize support for:

* Python
* Java
* JavaScript
* TypeScript
* Go

If the language is unclear, infer it from syntax. If unsure, say which language you are assuming.

---

## Workflow

Follow this workflow every time.

### Step 1: Understand the Code

Identify:

* Programming language
* Main function or module purpose
* Inputs and outputs
* Side effects, such as database writes, file operations, network calls, API calls, or state mutation
* External dependencies
* Expected behavior if described by the user

Write a short summary in plain language.

---

### Step 2: Identify Risk Areas

Review the code for:

* Logic bugs
* Missing input validation
* Boundary condition failures
* Null or None handling problems
* Empty input behavior
* Large input behavior
* Invalid input behavior
* Exception handling gaps
* Resource leaks
* Race conditions or concurrency issues
* Security risks
* Unclear naming or maintainability issues
* Hidden assumptions
* Incomplete return paths
* Incorrect error messages
* Potential performance issues

Do not invent risks that are not supported by the code. If a risk is speculative, mark it as `Possible`.

---

### Step 3: Apply Language-Specific Checks

#### Python Checks

Look for:

* Bare `except:`
* `except Exception` that silently ignores errors
* Missing `None` handling
* Dictionary access with `dict[key]` when key may be absent
* List or string indexing without boundary checks
* Division without zero check
* File open without context manager
* Mutable default arguments
* Use of `eval` or `exec`
* SQL query string concatenation
* Missing type hints for complex functions
* Functions that return inconsistent types

#### Java Checks

Look for:

* Possible `NullPointerException`
* `Optional.get()` without checking presence
* `List.get(index)` without bounds checking
* Division without zero check
* Catching broad `Exception` without proper handling
* Empty catch blocks
* SQL string concatenation
* Missing validation for public method parameters
* Mutable shared state
* Missing timeout or retry handling for external calls
* Inconsistent return values

#### JavaScript / TypeScript Checks

Look for:

* Missing null or undefined checks
* Promise rejection not handled
* Async function without try/catch where needed
* Array indexing without bounds checks
* Type coercion issues
* Use of `any` in TypeScript without reason
* Mutation of shared objects
* Missing validation for API input
* Unsafe dynamic code execution
* Inconsistent return types

#### Go Checks

Look for:

* Ignored errors
* Nil pointer risks
* Missing context timeout or cancellation
* Goroutine leaks
* Shared map access without synchronization
* Incorrect defer usage
* Incomplete input validation
* Returning zero values without explanation
* SQL string concatenation

---

### Step 4: Generate Test Cases

Generate tests that cover:

1. Happy path
2. Boundary inputs
3. Empty inputs
4. Null, None, or undefined inputs
5. Invalid inputs
6. Exception paths
7. Large inputs
8. Duplicate inputs
9. State changes
10. Regression cases for identified bugs

Each test case should include:

* Test name
* Input
* Expected output or behavior
* Why this test matters

If the user asks for actual unit test code, generate test code in the most appropriate framework.

Default frameworks:

* Python: `pytest`
* Java: `JUnit 5`
* JavaScript / TypeScript: `Jest`
* Go: built-in `testing` package

---

### Step 5: Decide Review Result

Classify the review as one of:

* `PASS`
* `NEEDS_CHANGES`
* `HIGH_RISK`

Use `HIGH_RISK` if:

* There is a security issue
* There is likely data loss
* There is likely production crash
* There is missing critical exception handling
* There is unsafe external command execution
* There is SQL injection risk
* There is a concurrency bug that may corrupt state

Use `NEEDS_CHANGES` if:

* There are medium-level bugs
* Important edge cases are missing
* Test coverage is weak
* Maintainability issues may cause future bugs
* Input validation is incomplete

Use `PASS` only if:

* No major risks are found
* Edge cases are reasonably handled
* Suggested tests cover the main behavior
* The implementation is understandable and maintainable

---

## Output Format

Always use the following output format.

````markdown
# Code Review Summary

## 1. What the Code Does

<Brief summary of the code behavior.>

## 2. Key Findings

| Severity | Type | Finding | Suggestion |
|---|---|---|---|
| HIGH / MEDIUM / LOW | BUG / EDGE_CASE / EXCEPTION / SECURITY / MAINTAINABILITY | <issue> | <fix> |

## 3. Edge Cases to Check

- <edge case 1>
- <edge case 2>
- <edge case 3>

## 4. Recommended Test Cases

| Test Name | Input | Expected Behavior | Reason |
|---|---|---|---|
| test_xxx | <input> | <expected> | <why it matters> |

## 5. Suggested Unit Test Code

```<language>
<unit test code if requested or useful>
````

## 6. Final Review Result

`PASS` / `NEEDS_CHANGES` / `HIGH_RISK`

## 7. Notes and Assumptions

* <Any assumption made due to missing context.>

````

If there are no obvious risks, still provide recommended tests and mention that the review is based only on the provided code.

---

## Quality Bar

A good review must:

- Be specific, not generic
- Point to actual code behavior
- Include actionable suggestions
- Cover both normal and abnormal paths
- Include boundary cases
- Avoid overclaiming
- Clearly separate confirmed issues from possible risks
- Generate tests that can realistically catch bugs
- Prefer simple and maintainable fixes
- Explain assumptions when context is missing

A bad review is one that:

- Only says “looks good”
- Only rewrites the code without explaining risks
- Ignores edge cases
- Generates tests that do not assert meaningful behavior
- Invents bugs not supported by the code
- Gives vague advice like “improve error handling” without saying how

---

## Example 1: Python Function

Input:

```python
def divide(a, b):
    return a / b
````

Expected review focus:

* Division by zero risk
* Type assumptions
* Normal path test
* Zero denominator test
* Negative number test
* Float input test

Recommended test cases:

| Test Name                    | Input            | Expected Behavior                                      | Reason                    |
| ---------------------------- | ---------------- | ------------------------------------------------------ | ------------------------- |
| test_divide_normal_case      | `divide(10, 2)`  | returns `5`                                            | Covers happy path         |
| test_divide_by_zero          | `divide(10, 0)`  | raises `ZeroDivisionError` or returns controlled error | Covers exception path     |
| test_divide_negative_numbers | `divide(-10, 2)` | returns `-5`                                           | Covers negative input     |
| test_divide_float_result     | `divide(5, 2)`   | returns `2.5`                                          | Covers non-integer result |

---

## Example 2: Java Optional Usage

Input:

```java
public String getUserName(Optional<User> user) {
    return user.get().getName();
}
```

Expected review focus:

* `Optional.get()` without presence check
* Possible `NoSuchElementException`
* Possible null name
* Missing behavior definition for absent user

Recommended fix:

```java
public String getUserName(Optional<User> user) {
    return user.map(User::getName).orElse("Unknown");
}
```

Recommended test cases:

| Test Name                          | Input                    | Expected Behavior | Reason            |
| ---------------------------------- | ------------------------ | ----------------- | ----------------- |
| shouldReturnUserNameWhenUserExists | Optional with valid user | returns name      | Happy path        |
| shouldReturnUnknownWhenUserMissing | Optional.empty()         | returns `Unknown` | Missing user path |
| shouldHandleNullName               | User with null name      | defined behavior  | Covers null field |

---

## Final Instruction for the Agent

When using this skill, behave like a practical code reviewer. Focus on correctness, edge cases, reliability, and testability.

Do not only generate code. First analyze the risks, then generate tests, then give a clear review result.
