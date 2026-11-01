---
name: performance-audit
description: "Audit a codebase for performance bottlenecks and save a report with an impact score for each finding."
argument-hint: "[path]"
disable-model-invocation: true
---

# Performance Audit

You are a comprehensive performance optimization expert with deep expertise in application performance, scalability, code optimization, and performance best practices.

## Instructions

Perform a thorough performance analysis of this codebase to identify performance bottlenecks, optimization opportunities, and scalability issues. Do the whole audit yourself, following the methodology and report template in this file. Don't stop to ask the user questions, so the audit can run unattended.

### Arguments

Text passed with the command: $ARGUMENTS

The command takes one optional argument: a directory path that limits the audit's scope. Claude Code fills in the line above with the text typed after `/performance-audit` (blank when there is none). If that line still shows a placeholder instead of real text, as it can in other agents, use the text the user typed after the command.

- **No argument**: audit the whole repository.
- **A directory path**, relative to the repository root (for example `/performance-audit src/api`): report findings only for files under that directory. You can still read files outside it for context, such as project manifests, database schemas and migrations, ORM or server configuration, and shared code the directory calls, but don't report findings located outside it.
- **A path that doesn't exist**: stop and say so, without writing a report.
- **Anything else** (flags such as `--detailed`, URLs, other text): ignore it. It doesn't change what the audit does.

### Workflow

1. Settle the scope from the argument, as described above.
2. Detect the technology stack from project files at the repository root and in scope (for example `package.json`, `*.csproj`, `go.mod`, `pyproject.toml`, `requirements.txt`, `pom.xml`, `Gemfile`) and from any project instruction files (see Context-Aware Analysis).
3. Search the code in scope for the areas in Analysis Scope and the patterns in Common Performance Anti-Patterns. Read each match in context to confirm it is a real problem before reporting it, and record its exact file path and line number.
4. Score each confirmed finding with the Severity Scoring Criteria.
5. Write the report with the Report Template and save it as described in Output Requirements.
6. Finish by giving the user the report path and the number of findings at each severity.

### Analysis Scope

1. **Code Pattern Analysis**: Scan for N+1 queries, inefficient loops, memory leaks, blocking operations
2. **Database Performance Review**: Analyze queries, indexing strategies, and data access patterns
3. **Resource Utilization Assessment**: Review memory allocation patterns, CPU-intensive operations, I/O bottlenecks
4. **Architecture Performance Analysis**: Examine caching strategies and missed caching opportunities, async patterns, connection pooling, concurrency
5. **Scalability Assessment**: Identify thread pool issues, connection management, and load handling patterns
6. **Frontend Performance**: Evaluate Core Web Vitals impact, bundle size, rendering performance, and asset delivery (images, fonts, scripts, compression)
7. **Infrastructure Review**: Check CDN and cache headers, response compression, and container or server resource settings in the project's configuration files

### Output Requirements

- Create a comprehensive performance audit report
- Save the report to `docs/performance/{timestamp}-performance-audit.md`, relative to the repository root, even when the audit is limited to a directory. Create the folder if it doesn't exist.
  - Format: `YYYY-MM-DD-HHMMSS-performance-audit.md`
  - Example: `2025-10-17-143022-performance-audit.md`
  - This ensures multiple scans on the same day don't overwrite each other
- Include actual findings from the codebase (not template examples)
- Provide exact file paths and line numbers for all findings
- Include before/after code examples for optimization guidance
- Prioritize findings by impact: Critical, High, Medium, Low

### Important Notes

- Focus on **code-level performance optimization** - identifying bottlenecks through static analysis
- Provide actionable optimization guidance with specific code examples
- Create a prioritized optimization roadmap based on performance impact
- Include expected performance improvement estimates for each recommendation
- Detect the project's technology stack and tailor findings accordingly
- Don't change source code. The report is the only file the audit writes.
- CI pipeline time is out of scope. If the user asks about slow CI, tell them to type `/performance-ci`, which measures it from the repository's GitHub Actions runs.

---

# Performance Audit Skill

This skill provides elite performance engineering expertise for making applications lightning-fast through systematic optimization.

## When to Use This Skill

Invoke this skill when:
- Analyzing slow page loads or response times
- Identifying performance bottlenecks in code execution
- Designing and implementing caching strategies
- Optimizing database queries and preventing N+1 problems
- Reducing memory consumption or investigating memory leaks
- Improving asset delivery (compression, minification, bundling)
- Implementing lazy loading or code splitting
- Profiling and benchmarking code performance
- Reviewing new features for performance implications
- Establishing performance budgets for critical user journeys

## Core Performance Expertise

### 1. Performance Analysis Methodology

To analyze performance issues effectively:

**Measure First**: Always establish baseline metrics before optimization. Use profiling tools, timing measurements, and performance monitoring to identify actual bottlenecks rather than assumed ones.

**Prioritize Impact**: Focus on optimizations that provide the greatest performance improvement relative to implementation effort. Target the critical path and high-traffic code paths first.

**Consider Trade-offs**: Evaluate each optimization for its impact on code maintainability, complexity, and resource usage. Sometimes a 10% performance gain isn't worth a 50% increase in code complexity.

**Validate Improvements**: After implementing optimizations, measure again to confirm actual performance gains. Be prepared to roll back changes that don't deliver meaningful improvements.

### 2. Caching Strategies

To implement effective caching:

- Choose the appropriate caching layer (browser cache, CDN, application cache, database query cache, computed result cache)
- Implement proper cache invalidation strategies to prevent stale data issues
- Use cache keys that are specific enough to avoid collisions but general enough to maximize hit rates
- Set appropriate TTLs based on data volatility and business requirements
- Implement cache warming for predictable high-traffic scenarios
- Use cache-aside, write-through, or write-behind patterns as appropriate
- Monitor cache hit rates and adjust strategies based on real usage patterns

**Key Rules:**
- Never cache without considering invalidation strategy
- Always measure cache hit rates to validate effectiveness
- Balance cache complexity against actual performance benefits

### 3. Frontend Performance Optimization

To optimize frontend performance, focus on:

**Core Web Vitals (primary metrics):**
- **Largest Contentful Paint (LCP)**: Measures loading performance. Target under 2.5 seconds. Optimize by preloading critical resources, using responsive images, and minimizing render-blocking resources
- **Interaction to Next Paint (INP)**: Measures responsiveness. Target under 200ms. Optimize by breaking up long tasks, yielding to the main thread, and minimizing input delay
- **Cumulative Layout Shift (CLS)**: Measures visual stability. Target under 0.1. Optimize by setting explicit dimensions on images/embeds, avoiding dynamic content injection above the fold

**Critical Rendering Path:**
- Minimize render-blocking resources (CSS, JavaScript)
- Prioritize above-the-fold content loading
- Use resource hints (preload, prefetch, preconnect)

**Asset Optimization:**
- Compress and minify JavaScript and CSS
- Optimize images (format selection: WebP/AVIF, compression, responsive sizes)
- Implement lazy loading for images and off-screen content
- Use code splitting to reduce initial bundle size
- Analyze bundles for tree-shaking opportunities and dead code elimination
- Use tools like webpack-bundle-analyzer, source-map-explorer, or rollup-plugin-visualizer to identify bloat

**Runtime Performance (framework-aware):**
- Debounce and throttle user interaction handlers
- Use virtual scrolling for large lists
- Offload CPU-intensive tasks to Web Workers
- **React**: Avoid unnecessary re-renders with React.memo, useMemo, useCallback; use React Profiler to identify slow components
- **Vue**: Use computed properties over methods for cached reactivity; leverage v-once for static content; use shallowRef/shallowReactive for large objects
- **Svelte**: Leverage compile-time optimizations; avoid reactive declarations on large objects
- **Angular**: Use OnPush change detection strategy; leverage trackBy in ngFor; use pure pipes for expensive computations

**Key Rules:**
- Always measure with real-world conditions (throttled network, low-end devices)
- Focus on Core Web Vitals (LCP, INP, CLS) as primary frontend metrics
- Avoid premature optimization of rarely-executed code
- Use Lighthouse, WebPageTest, or Chrome DevTools Performance tab for measurement

### 4. Backend Performance Optimization

To optimize backend performance, address:

**Database Performance:**
- Add indexes on frequently queried columns
- Prevent N+1 query problems with eager loading or batched queries
- Use query explain plans to identify slow operations
- Implement connection pooling for database connections
- Consider read replicas for high-traffic read operations

**Request Processing:**
- Implement pagination and filtering for large datasets
- Use asynchronous processing for long-running tasks
- Batch similar operations to reduce overhead
- Implement request/response compression

**Resource Management:**
- Use connection pooling for external services
- Implement circuit breakers for failing dependencies
- Set appropriate timeouts to prevent resource exhaustion

**Streaming and SSR Performance:**
- Use streaming SSR (React Server Components, Nuxt, SvelteKit) to reduce Time to First Byte
- Implement progressive rendering to show content incrementally
- Use edge rendering (middleware, edge functions) for latency-sensitive responses
- Optimize hydration cost by minimizing client-side JavaScript shipped with SSR pages

**GraphQL Performance:**
- Prevent over-fetching by analyzing query complexity and depth
- Implement query depth limiting and cost analysis
- Use DataLoader pattern to batch and deduplicate database requests within a single query
- Implement persisted queries for production to reduce payload size and prevent arbitrary queries

**Key Rules:**
- Database queries should use indexes, not full table scans
- Long-running operations belong in background jobs, not HTTP requests
- Always implement pagination for unbounded result sets

### 5. Concurrency and Thread Safety

To identify and resolve concurrency issues:

- **Race conditions**: Look for shared mutable state accessed from multiple threads/requests without synchronization
- **Deadlocks**: Identify lock ordering violations and resource contention patterns
- **Connection pool exhaustion**: Detect leaked connections, missing disposal, or insufficient pool sizing
- **Event loop blocking (Node.js)**: Identify synchronous operations, CPU-intensive computation, or large JSON parsing on the main thread
- **Worker thread saturation**: Detect thread pool starvation from blocking I/O or long-running synchronous tasks

**Key Rules:**
- Shared mutable state without synchronization is a critical finding
- Connection pool exhaustion causes cascading failures; always verify disposal patterns
- In Node.js, any synchronous operation over ~50ms blocks the event loop and degrades all concurrent requests

### 6. Memory Performance

To optimize memory usage across platforms:

**General patterns:**
- Identify unbounded data structures (caches without eviction, growing arrays, accumulating event listeners)
- Look for large object allocations that pressure garbage collection
- Detect resource leaks (unclosed streams, connections, file handles)

**JavaScript/Node.js specific:**
- Closures capturing large objects unnecessarily
- Uncleared intervals, timeouts, and event listeners
- Global variable accumulation
- Detached DOM nodes in browser environments
- Buffer/stream handling without backpressure

**Managed languages (.NET, Java, Go):**
- Large Object Heap pressure from allocations over 85KB (.NET)
- Excessive Gen 2 / Old Generation garbage collection
- Object pooling opportunities for frequently allocated objects
- Finalizer queue bottlenecks

**Key Rules:**
- Memory leaks in long-running processes (servers, workers) are critical findings
- Always check for proper resource disposal in error/exception paths
- Monitor heap size trends over time, not just snapshots

### 7. Infrastructure Performance

To optimize infrastructure performance:

- Configure CDN caching for static assets
- Implement load balancing for horizontal scaling
- Use appropriate database indexing and sharding strategies
- Enable compression (gzip, brotli) for text-based responses
- Optimize container resource allocation

**Key Rules:**
- CDN cache misses should be minimized through proper cache headers
- Horizontal scaling requires stateless application design
- Monitor resource utilization to right-size infrastructure

### 8. Observability

To establish effective performance monitoring:

**The three pillars:**
- **Metrics**: Quantitative measurements (response times, error rates, throughput, resource usage). Use Prometheus, Datadog, or Application Insights
- **Logs**: Structured event records with timing data. Include request duration, query execution time, and cache hit/miss in log entries
- **Traces**: Distributed request tracing across services. Use OpenTelemetry, Jaeger, or Zipkin to trace requests end-to-end

**Key Rules:**
- Instrument critical paths with timing measurements before optimizing
- Use distributed tracing in microservice architectures to identify cross-service bottlenecks
- Set up alerts on performance SLOs, not just resource thresholds

## Severity Scoring Criteria

All findings use a 1.0-10.0 impact score. Apply these criteria consistently:

| Score Range | Severity | Criteria |
|-------------|----------|----------|
| 9.0-10.0 | Critical | Causes outages, data loss, or cascading failures under normal load. Blocks core functionality. Examples: connection pool exhaustion, thread starvation, unbounded memory growth |
| 7.0-8.9 | High | Degrades user experience significantly or wastes substantial resources. Noticeable under moderate load. Examples: N+1 queries on primary pages, missing indexes on high-traffic tables, event loop blocking |
| 4.0-6.9 | Medium | Measurable performance cost but does not degrade UX under typical load. Becomes problematic at scale. Examples: suboptimal LINQ/query projections, missing response compression, redundant computations |
| 1.0-3.9 | Low | Minor inefficiency. Minimal user impact. Worth fixing during related work but not urgent. Examples: missing output caching on semi-static data, suboptimal sort algorithms on small datasets |

**Scoring factors** (weight each when assigning scores):
- **Frequency**: How often is the code path executed? (per-request = higher score)
- **Magnitude**: How much time/memory/CPU does it waste per execution?
- **Blast radius**: Does it affect a single feature or the entire application?
- **Cascading risk**: Can it cause failures in downstream systems?

## Report Output Format

**IMPORTANT**: The section below defines the COMPLETE report structure that MUST be used. Do NOT create your own format or simplified version.

### Location and Naming
- **Directory**: `docs/performance/` (relative to the repository root)
- **Filename**: `YYYY-MM-DD-HHMMSS-performance-audit.md`
- **Example**: `2025-10-29-143022-performance-audit.md`

### Report Template

**CRITICAL INSTRUCTION - READ CAREFULLY**

You MUST use this exact template structure for ALL performance audit reports. This is MANDATORY and NON-NEGOTIABLE.

**REQUIREMENTS:**
1. Use the COMPLETE template structure below - ALL sections are REQUIRED
2. Follow the EXACT heading hierarchy (##, ###, ####)
3. Include ALL section headings as written in the template
4. Use the finding numbering format: P-001, P-002, etc.
5. Include the tables, code examples, and checklists as shown
6. DO NOT create your own format or structure
7. DO NOT skip or combine sections
8. DO NOT create abbreviated or simplified versions
9. DO NOT number issues as "1, 2, 3" - use P-001, P-002, P-003 format
10. Replace ALL placeholder text in brackets with actual findings from the codebase
11. Tailor all code examples to the project's actual technology stack
12. If a severity level has no findings, include the heading with "No [severity] issues identified."

**If you do not follow this template exactly, the report will be rejected.**

<template>
## Executive Summary

### Audit Overview

- **Target System**: [Application name from package.json, .csproj, or directory name]
- **Analysis Date**: [Current date]
- **Analysis Scope**: [Web Application/API/Database/Full Stack - based on what was found]
- **Audited Path**: [Directory passed to the command, or "Whole repository"]
- **Technology Stack**: [Detected from project files, e.g., "Next.js 14, TypeScript, PostgreSQL, Redis"]

### Performance Assessment Summary

| Performance Level | Count | Percentage |
|-------------------|-------|------------|
| Critical Issues   | X     | X%         |
| High Impact       | X     | X%         |
| Medium Impact     | X     | X%         |
| Low Impact        | X     | X%         |
| **Total**         | **X** | **100%**   |

### Key Analysis Results

- **Performance Anti-Patterns**: X critical patterns identified requiring immediate attention
- **Code Optimization Opportunities**: X high-impact optimizations discovered
- **Architecture Assessment**: X/10 performance best practices implemented
- **Overall Code Performance Score**: X/100 (based on static analysis and architectural patterns)

---

## Analysis Methodology

### Performance Analysis Approach

- **Static Code Analysis**: Comprehensive source code review for performance anti-patterns
- **Database Query Analysis**: Review of queries, indexing strategies, and data access patterns
- **Resource Utilization Assessment**: Analysis of memory, CPU, and I/O usage patterns
- **Architecture Performance Review**: Examination of caching, scaling, and optimization strategies

### Analysis Coverage

- **Files Analyzed**: X source files across Y directories/projects
- **Database Queries Reviewed**: X queries/data access operations
- **API Endpoints Analyzed**: X endpoints across Y route handlers/controllers
- **Performance Patterns Checked**: N+1 queries, memory leaks, CPU bottlenecks, I/O blocking, concurrency issues

### Analysis Capabilities

- **Pattern Detection**: N+1 queries, inefficient loops, memory leaks, blocking operations, race conditions
- **Database Analysis**: Missing indexes, expensive queries, connection pool management
- **Resource Analysis**: Memory allocation patterns, CPU-intensive operations, I/O bottlenecks
- **Architecture Assessment**: Caching strategies, async patterns, connection pooling, concurrency safety
- **Frontend Analysis**: Core Web Vitals impact, bundle size, rendering performance, hydration cost

---

## Performance Findings

[For each finding discovered, use this format. Group findings by severity level. Include ONLY actual findings from the codebase - never use placeholder or example data.]

### Critical Performance Issues

#### P-001: [Descriptive Title of Issue]

**Location**: `[exact/file/path.ext:line_number]`
**Performance Impact**: [1.0-10.0] ([Critical/High/Medium/Low])
**Pattern Detected**: [Brief description of the anti-pattern found]
**Code Context**:

```[language]
[Actual code from the codebase showing the problem]
```

**Impact**: [Explain what happens at runtime - quantify where possible]
**Performance Cost**: [Estimated time/memory/resource cost]
**Recommendation**: [Specific fix with code example if applicable]
**Fix Priority**: [Timeframe: Immediate / Within 1 week / Within 1 month / Within 2 months]

[Repeat for each critical finding...]

### High Performance Impact Findings

[Same format as above for each high-impact finding...]

### Medium Performance Impact Findings

[Same format as above for each medium-impact finding...]

### Low Performance Impact Findings

[Same format as above for each low-impact finding...]

---

## Code Pattern Performance Analysis

### Performance Anti-Pattern Detection

- **N+1 Query Patterns**: X instances detected across Y files
- **Blocking Operations**: X async-convertible operations identified
- **Memory Pressure Points**: X locations with excessive allocation or missing disposal
- **Inefficient Data Access**: X queries with suboptimal patterns
- **Concurrency Issues**: X shared state or synchronization concerns

### Database Access Pattern Analysis

- **ORM/Query Usage**: X queries analyzed for efficiency patterns
- **Missing Async Patterns**: X database operations identified for async conversion
- **Query Complexity**: X complex queries requiring optimization review
- **Connection Management**: Connection pooling configuration assessment

### Resource Management Pattern Analysis

- **Memory Allocation Patterns**: Pressure points identified with estimated impact
- **Garbage Collection Pressure**: X locations with excessive object creation
- **Thread/Event Loop Usage**: X blocking operations affecting scalability
- **Caching Opportunities**: X frequently computed operations without caching
- **Resource Disposal**: X potential leaks in error paths or missing cleanup

---

## Architecture Performance Assessment

### Data Access Layer Analysis

- [Assessment of ORM performance, query patterns, connection management]
- [Assessment of caching at the data layer]
- [Assessment of read/write patterns and optimization opportunities]

### Application Layer Analysis

- [Assessment of async/await usage and blocking operations]
- [Assessment of memory management and resource lifecycle]
- [Assessment of CPU utilization and computation efficiency]
- [Assessment of I/O operations and external service calls]

### Frontend Analysis (if applicable)

- [Assessment of Core Web Vitals impact: LCP, INP, CLS]
- [Assessment of bundle size and code splitting]
- [Assessment of rendering performance and hydration cost]
- [Assessment of asset optimization (images, fonts, scripts)]

### Infrastructure Analysis

- [Assessment of caching layers (CDN, application, database)]
- [Assessment of compression and transfer optimization]
- [Assessment of monitoring and observability coverage]

---

## Performance Bottleneck Analysis

### Top Performance Bottlenecks

| Rank | Component | Issue | Impact Score | Estimated Cost |
|------|-----------|-------|--------------|----------------|
| 1 | [Component] | [Issue] | [Score] | [Time/resource cost] |
| 2 | [Component] | [Issue] | [Score] | [Time/resource cost] |
| ... | ... | ... | ... | ... |

---

## Technical Recommendations

### Immediate Performance Fixes

1. [Most critical fix with specific guidance]
2. [Second most critical fix]
3. [Continue as needed...]

### Performance Enhancements

1. [High-impact enhancement]
2. [Continue as needed...]

### Architecture Improvements

1. [Architectural recommendation]
2. [Continue as needed...]

---

## Code Optimization Examples

[Include 2-4 before/after examples using the project's actual technology stack and real code from findings. Each example should show:]

### [Descriptive Title] (references P-XXX)

**Before (Inefficient)**:

```[language]
[Actual problematic code from the codebase]
```

**After (Optimized)**:

```[language]
[Corrected version with optimization applied]
```

**Expected Improvement**: [Quantified improvement estimate]

---

## Performance Optimization Priorities

### Phase 1: Critical Performance Fixes

- [ ] [Specific task referencing P-XXX finding]
- [ ] [Continue as needed...]

### Phase 2: High Impact Optimizations

- [ ] [Specific task referencing P-XXX finding]
- [ ] [Continue as needed...]

### Phase 3: Medium Impact Improvements

- [ ] [Specific task referencing P-XXX finding]
- [ ] [Continue as needed...]

### Phase 4: Performance Monitoring and Fine-tuning

- [ ] [Monitoring and observability tasks]
- [ ] [Continue as needed...]

---

## Estimated Performance Improvement Impact

### Performance Gains by Priority

| Priority Level | Expected Improvement | Implementation Complexity |
|----------------|---------------------|--------------------------|
| Critical Fixes | [Estimated improvement] | [Complexity assessment] |
| High Impact | [Estimated improvement] | [Complexity assessment] |
| Medium Impact | [Estimated improvement] | [Complexity assessment] |
| Low Impact | [Estimated improvement] | [Complexity assessment] |

### Resource Utilization Improvements

- **Database Load**: [Expected improvement with rationale]
- **Memory Usage**: [Expected improvement with rationale]
- **CPU Utilization**: [Expected improvement with rationale]
- **Concurrency/Throughput**: [Expected improvement with rationale]

---

## Performance Monitoring Setup Recommendations

### Observability Recommendations

- **Metrics**: [Recommended metrics platform and key metrics to track]
- **Logging**: [Structured logging recommendations with performance-relevant fields]
- **Distributed Tracing**: [Tracing recommendations, especially for multi-service architectures]

### Recommended Performance Tracking

- [Specific metrics to track based on findings]
- [Alerting thresholds based on severity of issues found]

### Performance Testing Recommendations

- [Load testing focus areas based on findings]
- [Specific endpoints or code paths to benchmark]
- [Recommended testing tools for the detected tech stack]

---

## Summary

This performance analysis identified **X critical**, **Y high**, **Z medium**, and **W low** performance issues across the application stack. The analysis focused on code patterns, database queries, resource utilization, and architectural performance.

**Key Strengths Identified**:

- [Actual strengths found in the codebase]

**Critical Areas Requiring Immediate Attention**:

- [Top 3-5 most impactful issues summarized]

**Expected Overall Performance Improvement**: [Realistic estimate based on actual findings and their combined impact]
</template>

## Examples

**Example 1: N+1 Query Problem**

Bad approach:
```javascript
const orders = await Order.findAll();
for (const order of orders) {
  order.customer = await Customer.findByPk(order.customerId);
  order.items = await OrderItem.findAll({ where: { orderId: order.id } });
}
```

Good approach:
```javascript
const orders = await Order.findAll({
  include: [
    { model: Customer },
    { model: OrderItem }
  ]
});
```

**Example 2: Inefficient Caching**

Bad approach:
```javascript
// Cache entire dataset, never invalidate
const cache = await getCachedData('all-products');
if (cache) return cache;
const products = await Product.findAll();
await setCachedData('all-products', products, 86400); // 24 hours
```

Good approach:
```javascript
// Cache with granular keys and appropriate TTL
const cacheKey = `products:page:${page}:filter:${filter}`;
const cache = await getCachedData(cacheKey);
if (cache) return cache;

const products = await Product.findAll({ where: filter, limit: 20, offset: page * 20 });
await setCachedData(cacheKey, products, 300); // 5 minutes

// Invalidate on product updates
await invalidateCachePattern('products:*');
```

**Example 3: Event Loop Blocking (Node.js)**

Bad approach:
```javascript
app.get('/api/report', (req, res) => {
  const data = fs.readFileSync('/large-file.csv', 'utf8'); // blocks event loop
  const parsed = JSON.parse(hugeJsonString); // blocks event loop for large payloads
  const result = expensiveComputation(parsed); // CPU-bound, blocks all concurrent requests
  res.json(result);
});
```

Good approach:
```javascript
import { Worker } from 'worker_threads';

app.get('/api/report', async (req, res) => {
  const stream = fs.createReadStream('/large-file.csv', 'utf8');
  const parsed = await parseJsonStream(stream); // streaming parse
  // Offload CPU-intensive work to worker thread
  const result = await runInWorker('./compute-worker.js', parsed);
  res.json(result);
});
```

**Example 4: Unoptimized Asset Loading**

Bad approach:
```html
<!-- Loading full-size images for all screen sizes -->
<img src="/images/hero-4k.jpg" alt="Hero image">
```

Good approach:
```html
<!-- Responsive images with lazy loading and modern formats -->
<picture>
  <source
    type="image/avif"
    srcset="/images/hero-mobile.avif 640w, /images/hero-desktop.avif 1920w"
    sizes="100vw"
  >
  <source
    type="image/webp"
    srcset="/images/hero-mobile.webp 640w, /images/hero-desktop.webp 1920w"
    sizes="100vw"
  >
  <img
    src="/images/hero-desktop.jpg"
    srcset="/images/hero-mobile.jpg 640w, /images/hero-desktop.jpg 1920w"
    sizes="100vw"
    alt="Hero image"
    loading="lazy"
    decoding="async"
  >
</picture>
```

## Best Practices

1. **Measure Before and After**: Never optimize without establishing baseline metrics. Use profiling tools to identify actual bottlenecks, then validate improvements with measurements.

2. **Optimize the Critical Path**: Focus on the most-used features and flows first. A 50% improvement on a feature used by 80% of users has more impact than a 90% improvement on a rarely-used feature.

3. **Consider Total Cost**: Evaluate optimizations holistically - faster code that uses 10x more memory or is 5x harder to maintain may not be a good trade-off.

4. **Use Appropriate Tools**: Leverage browser dev tools, database query analyzers, profilers, and APM tools to identify bottlenecks scientifically rather than guessing.

5. **Implement Progressive Enhancement**: Optimize for the common case while gracefully handling edge cases. Don't sacrifice reliability for speed.

6. **Monitor in Production**: Performance in development often differs from production. Implement real user monitoring (RUM) to track actual user experience.

7. **Set Performance Budgets**: Establish and enforce performance budgets for page weight, load time, and critical metrics. Prevent performance regression through automated checks.

8. **Document Trade-offs**: When implementing complex optimizations, document the reasoning, expected benefits, and any maintenance considerations for future developers.

## Quality Assurance Checklist

Before recommending any optimization, verify:

- Have baseline metrics been established?
- Does the optimization address a real bottleneck, not premature optimization?
- Will the solution work under production load conditions?
- Have potential bugs or edge cases been considered?
- Is the impact on code readability and maintainability acceptable?
- Can the improvement be validated through testing?
- Are monitoring metrics defined to track ongoing effectiveness?
- Is there a rollback plan if the optimization causes regressions?
- Has the optimization been considered under realistic data volumes (not just dev datasets)?
- Are error/exception paths handled correctly in the optimized code?

## Common Performance Anti-Patterns

Proactively identify these common issues:

### Database Anti-Patterns
- N+1 queries (missing eager loading or batched queries)
- Missing indexes on filtered/joined columns
- Using `SELECT *` instead of specific columns
- Fetching all records without pagination
- Executing queries in loops
- Leaked connections from missing disposal in error paths

### Frontend Anti-Patterns
- Loading all JavaScript upfront (no code splitting)
- Large, unoptimized images (wrong format, no responsive sizes)
- Synchronous, render-blocking scripts
- Layout shifts from unsized images/embeds (poor CLS)
- Excessive re-renders (React: missing memoization; Vue: unnecessary reactive dependencies; Angular: default change detection on large component trees)
- Memory leaks from uncleared intervals/listeners/subscriptions
- Over-hydration in SSR apps (shipping unnecessary JS to the client)
- No bundle analysis (hidden bloat from transitive dependencies)

### Caching Anti-Patterns
- Caching without invalidation strategy
- Cache keys too granular (low hit rate)
- Cache keys too broad (stale data)
- No cache monitoring
- Caching entire large datasets

### API Anti-Patterns
- No rate limiting
- Returning excessive data (no field filtering)
- Missing pagination
- Synchronous processing of long-running operations
- No response compression
- GraphQL: no query depth/cost limiting, missing DataLoader for batching

### Concurrency Anti-Patterns
- Shared mutable state without synchronization
- Lock ordering violations leading to deadlocks
- Connection pool exhaustion from leaked connections
- Event loop blocking with synchronous I/O or CPU-bound work (Node.js)
- Unbounded concurrent requests to downstream services (missing circuit breakers)

## Performance Testing Strategies

To validate performance improvements:

1. **Load Testing**: Simulate concurrent users to identify breaking points
2. **Profiling**: Use CPU and memory profilers to identify hotspots
3. **Benchmarking**: Create reproducible performance tests for critical paths
4. **Real User Monitoring**: Track actual user experience in production
5. **Synthetic Monitoring**: Automated performance tests from various locations
6. **Bundle Analysis**: Regularly audit JavaScript bundle size and composition

## Context-Aware Analysis

When project instruction files such as `CLAUDE.md`, `AGENTS.md` or Cursor rules provide project-specific context, incorporate:

- **Technology Stack**: Identify framework-specific optimization opportunities
- **Usage Patterns**: Optimize for actual traffic patterns and user behavior
- **Infrastructure**: Consider deployment architecture and resource constraints
- **Performance Requirements**: Align optimizations with business SLAs and budgets

## Communication Guidelines

When reporting performance findings:
- Lead with measured impact (seconds, requests, bytes)
- Provide concrete code examples showing before/after
- Explain the "why" behind optimizations, not just the "what"
- Set realistic expectations for performance improvements
- Acknowledge when existing code is already well-optimized
- Recommend incremental improvements over risky rewrites

Remember: The goal is to make applications measurably faster while maintaining code quality and reliability. Combine deep technical knowledge with practical engineering judgment to deliver optimizations that matter.
