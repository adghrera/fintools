import { error } from '@sveltejs/kit';

/** @type {import('./$types').PageLoad} */
export function load({ params }) {
    if (params.slug === 'hello') {
        return {
            post: {
                title: `Title for ${params.slug} goes here`,
                content: `Content for ${params.slug} goes here`
            }
        };
    }

    error(404, 'Not found');
}

// export const prerender = true or false or 'auto'
// export const ssr = true or false
// export const csr = true or false