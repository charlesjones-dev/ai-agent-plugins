# Assessment Categories

What to check in each of the 12 modernization categories. Check only the categories the audit configuration selects, and apply the applicability rule in SKILL.md when all categories are selected.

## 1. SOLID/DRY/KISS Violations

Examine for engineering principle violations:

**Single Responsibility Principle (SRP):**
- Classes/modules with more than one reason to change
- Components handling both UI rendering and business logic
- Route handlers containing database queries, validation, and response formatting
- Utility files that have grown into "God objects" with unrelated functions

**Open/Closed Principle (OCP):**
- Code that requires modification (not extension) to add new features
- Switch/if-else chains that grow with each new variant instead of using polymorphism or strategy patterns
- Hardcoded behavior that should be configurable or pluggable

**Liskov Substitution Principle (LSP):**
- Subclasses that break the contract of their parent class
- Interface implementations that throw "not implemented" for required methods
- Overridden methods that change expected behavior

**Interface Segregation Principle (ISP):**
- Large interfaces forcing implementors to depend on methods they don't use
- Props interfaces in React/Vue components that are excessively broad
- Service interfaces with dozens of methods instead of focused, cohesive contracts

**Dependency Inversion Principle (DIP):**
- High-level modules directly importing low-level implementation details
- Direct database client usage in business logic instead of repository abstractions
- Hardcoded dependencies instead of injection or configuration

**DRY (Don't Repeat Yourself):**
- Copy-pasted code blocks across multiple files with minor variations
- Duplicated validation logic between client and server with no shared schema
- Repeated query patterns that should be extracted into shared data access functions
- Similar component structures that could be generalized with props/slots

**KISS (Keep It Simple, Stupid):**
- Over-engineered abstractions for simple operations (factory patterns for single implementations)
- Unnecessary design patterns that add complexity without benefit
- Complex generic types where simple types would suffice
- Premature optimization that reduces readability

**YAGNI (You Aren't Gonna Need It):**
- Feature flags for features that were never implemented
- Abstract base classes with only one concrete implementation
- Configuration options that no one uses or changes
- Commented-out code preserved "just in case"

## 2. Type Safety & Language Misuse

Examine for type system and language idiom issues:

**TypeScript-specific:**
- Overuse of `any` type (especially `as any` assertions to silence errors)
- Missing or overly broad type definitions (e.g., `Record<string, any>`)
- Type assertions (`as Type`) instead of proper type narrowing with guards
- Incorrect generic type parameters or missing generic constraints
- Using `interface` vs `type` inconsistently without clear convention
- Missing discriminated unions for state management (using boolean flags instead)
- Non-strict TypeScript configuration (`strict: false` or missing strict checks)
- Using `!` (non-null assertion) to suppress null checks instead of handling nullability

**JavaScript-specific:**
- Using `var` instead of `const`/`let`
- Missing optional chaining (`?.`) and nullish coalescing (`??`)
- Using `==` instead of `===` for comparisons
- Callback hell instead of async/await
- Not using destructuring where appropriate

**C#/.NET-specific:**
- Not using nullable reference types
- Using `dynamic` instead of proper typing
- Missing `IDisposable` / `using` patterns for resource management
- Synchronous I/O in async contexts (blocking the thread pool)

**Python-specific:**
- Missing type hints (PEP 484)
- Using mutable default arguments
- Not using f-strings (using .format() or % formatting)
- Ignoring context managers for resource handling

## 3. Error Handling

Examine for error handling quality:

- **Empty catch blocks**: `catch (e) {}` or `catch { }` that silently swallow errors
- **Generic catch-all**: Single try/catch wrapping entire functions without specific error handling
- **Console.log as error handling**: Using `console.log(error)` or `console.error(error)` without proper error propagation, reporting, or recovery
- **Missing error boundaries**: React/Vue applications without error boundary components
- **No graceful degradation**: Features that crash entirely instead of falling back
- **Inconsistent error shapes**: Different error formats across the codebase (sometimes strings, sometimes objects, sometimes Error instances)
- **Missing async error handling**: Unhandled promise rejections, missing `.catch()` on promises, no try/catch in async functions
- **Error message information leakage**: Exposing stack traces, internal paths, or database errors to end users
- **Missing retry logic**: Network calls and external service calls with no retry/backoff strategy
- **No error logging/monitoring**: No structured error logging for production debugging (no Sentry, no error tracking)

## 4. Security Anti-patterns

Examine for security issues commonly introduced by older AI models:

- **Hardcoded secrets**: API keys, tokens, passwords, or connection strings in source code
- **Missing input validation**: User input passed directly to database queries, file system operations, or shell commands
- **SQL/NoSQL injection**: String concatenation in queries instead of parameterized queries
- **XSS vulnerabilities**: Rendering user input without sanitization (using `dangerouslySetInnerHTML`, `v-html`, or template literals in HTML)
- **Missing CORS configuration**: No CORS headers or overly permissive `Access-Control-Allow-Origin: *`
- **Insecure authentication**: Storing passwords in plaintext or with weak hashing (MD5, SHA1), missing session expiration
- **Missing rate limiting**: API endpoints without rate limiting allowing brute force or abuse
- **Insecure defaults**: Debug mode enabled, verbose error messages in production, exposed admin panels
- **Missing CSRF protection**: Forms and state-changing endpoints without CSRF tokens
- **Insecure cookie settings**: Missing `HttpOnly`, `Secure`, or `SameSite` flags on session cookies
- **Path traversal**: File operations using user input without path sanitization
- **Missing security headers**: No CSP, HSTS, X-Frame-Options, or X-Content-Type-Options headers

## 5. Performance Anti-patterns

Examine for performance issues older models commonly introduced:

- **N+1 queries**: Fetching related data in loops instead of using joins or eager loading
- **Missing pagination**: Fetching entire datasets without limit/offset or cursor-based pagination
- **Synchronous bottlenecks**: Using `readFileSync`, blocking I/O, or CPU-bound work on the main thread/event loop
- **Full library imports**: `import _ from 'lodash'` instead of `import debounce from 'lodash/debounce'`
- **Missing database indexes**: Queries filtering on columns without indexes
- **No caching strategy**: Repeated expensive computations or API calls without caching
- **Memory leaks**: Uncleared intervals/timeouts, growing arrays, unclosed connections, event listener accumulation
- **Unnecessary re-renders**: Missing React.memo, useMemo, useCallback; Vue components with unnecessary reactive dependencies
- **Large bundle sizes**: No code splitting, no lazy loading, importing entire icon libraries
- **Missing compression**: No gzip/brotli for API responses or static assets
- **Inefficient data structures**: Using arrays where Sets/Maps would be O(1) instead of O(n)
- **Missing connection pooling**: Creating new database connections per request instead of pooling

## 6. Testing Gaps

Examine for testing quality issues:

- **Implementation-coupled tests**: Tests that break when refactoring internal code without changing behavior
- **Over-mocking**: Mocking so much that tests don't verify real behavior (testing mocks, not code)
- **Missing edge cases**: Only testing happy paths, ignoring error cases, boundary values, and empty states
- **No integration tests**: Only unit tests exist, missing tests for component interactions and data flows
- **Snapshot abuse**: Over-reliance on snapshot tests without meaningful assertions
- **Test data hardcoding**: Hardcoded test data that doesn't represent real-world scenarios
- **Missing async test handling**: Tests that don't properly await async operations (false positives)
- **No test isolation**: Tests that depend on execution order or share mutable state
- **Missing API contract tests**: No tests validating request/response shapes for API endpoints
- **Flaky tests**: Tests with race conditions, timing dependencies, or external service dependencies

## 7. Architecture Debt

Examine for architectural quality issues:

- **Tight coupling**: Components/modules directly depending on concrete implementations instead of abstractions
- **Circular dependencies**: Module A imports from B, B imports from A (or longer cycles)
- **Business logic in UI**: Validation rules, calculations, or data transformations in component render logic
- **Missing abstraction layers**: Direct database access from route handlers without service/repository layers
- **God files**: Single files with 500+ lines containing unrelated functionality
- **Inconsistent patterns**: Different architectural approaches used for similar features (some with services, some without)
- **Missing separation of concerns**: API routes handling validation, business logic, data access, and response formatting
- **No dependency injection**: Hardcoded dependencies making testing and swapping implementations difficult
- **Barrel file bloat**: index.ts re-export files that pull in the entire module graph
- **Missing domain modeling**: Using primitive types everywhere instead of domain-specific types (string for email, number for currency)

## 8. Frontend Debt

Examine for frontend-specific issues (when applicable):

- **Prop drilling**: Passing props through multiple intermediate components instead of using context, stores, or composition
- **State management anti-patterns**: Storing derived state, duplicating state across components, global state for local concerns
- **useEffect misuse (React)**: Using useEffect for derived state, missing dependency arrays, or as an event handler
- **Inline styles everywhere**: Using style attributes instead of CSS classes, modules, or styled-components
- **Missing accessibility**: No alt text, missing ARIA attributes, non-semantic HTML, no keyboard navigation
- **No responsive design**: Fixed pixel widths, no media queries, no mobile consideration
- **CSS anti-patterns**: `!important` overuse, deeply nested selectors, no CSS custom properties, no design tokens
- **Missing loading states**: No skeleton screens, spinners, or loading indicators for async operations
- **No error UI**: Missing error states, fallback UI, or user-friendly error messages
- **Client-side data fetching anti-patterns**: Fetching in useEffect without cleanup, no request deduplication, no caching (should use SWR/React Query/TanStack Query pattern)

## 9. Dependency Health

Examine for dependency management issues:

- **Deprecated packages**: Using packages that are no longer maintained or have been superseded
- **Vulnerable versions**: Dependencies with known CVEs that have patches available
- **Unnecessary dependencies**: Packages imported for trivial functionality that could be a few lines of code
- **Missing lock files**: No package-lock.json, yarn.lock, or pnpm-lock.yaml committed
- **Version range risks**: Using `*` or very loose version ranges (`^` on major 0.x packages)
- **Duplicate functionality**: Multiple packages solving the same problem (e.g., both axios and node-fetch)
- **Missing peer dependency warnings**: Peer dependency conflicts that could cause runtime issues
- **Dev dependencies in production**: devDependencies leaking into production bundles
- **Abandoned packages**: Dependencies with no updates in 2+ years and open security issues

## 10. AI Hallucination Artifacts

Examine for artifacts specific to AI-generated code:

- **Non-existent APIs**: Calls to methods, functions, or properties that don't exist on the library being used
- **Wrong function signatures**: Calling functions with incorrect parameter order, types, or count
- **Hallucinated packages**: Import statements for npm/pip/nuget packages that don't exist
- **Incorrect framework patterns**: Using patterns from one framework version in another (e.g., React class component patterns in a hooks codebase)
- **Fabricated configuration options**: Config properties that aren't supported by the tool or framework
- **Mixed-up library APIs**: Using the API of one library while importing another (e.g., Express middleware patterns in Fastify)
- **Deprecated method usage**: Using methods that were deprecated or removed in the installed version
- **Incorrect type definitions**: Custom type definitions that don't match the actual library types
- **Phantom environment variables**: References to environment variables that are never defined or documented
- **Dead code from failed attempts**: Commented-out or unreachable code blocks from prior AI generation attempts that were never cleaned up

## 11. Modern Pattern Gaps

Examine for opportunities to adopt modern patterns:

- **Missing modern JavaScript syntax**: Not using optional chaining (`?.`), nullish coalescing (`??`), logical assignment (`??=`, `||=`, `&&=`), or `Array.at()`
- **Outdated async patterns**: Using callbacks or `.then()` chains instead of async/await
- **Legacy CSS**: Using floats for layout instead of Flexbox/Grid, vendor prefixes for widely supported properties
- **Old build tooling**: Using Webpack 4 when Vite, esbuild, or Turbopack are appropriate
- **Missing modern web APIs**: Not using Fetch API, Intersection Observer, AbortController, structuredClone, or Web Streams
- **Legacy state management**: Using Redux boilerplate when Zustand, Jotai, or Pinia would be simpler
- **Missing server components**: Not leveraging React Server Components or equivalent SSR patterns where beneficial
- **Outdated Node.js APIs**: Using `fs.readFile` with callbacks instead of `fs.promises`, missing `node:` protocol prefix
- **Missing modern .NET patterns**: Not using minimal APIs, record types, or pattern matching (C#)
- **Legacy Python patterns**: Not using match statements (3.10+), walrus operator (3.8+), or dataclasses

## 12. Configuration & DevOps Debt

Examine for configuration and operational readiness issues:

- **Hardcoded configuration**: URLs, ports, feature flags, or thresholds hardcoded instead of environment-driven
- **Missing environment validation**: No runtime validation that required environment variables are set (missing something like envalid, zod env parsing, or manual checks)
- **No health check endpoints**: Missing `/health` or `/readyz` endpoints for container orchestration
- **Missing .env.example**: No documentation of required environment variables
- **Poor Dockerfile practices**: Running as root, not using multi-stage builds, copying unnecessary files, not using .dockerignore
- **Missing CI/CD configuration**: No automated testing, linting, or deployment pipelines
- **No logging strategy**: Using console.log in production instead of structured logging (pino, winston, serilog)
- **Missing monitoring/alerting**: No application performance monitoring, error tracking, or alerting setup
- **Insecure secret management**: Secrets in .env files committed to version control or missing from .gitignore
- **Missing database migrations**: Schema changes applied manually instead of through migration files
