import { z } from 'zod';
import type { FastifyPluginAsyncZod } from 'fastify-type-provider-zod';
import { main } from '../langchain';

const MESSAGE_SCHEMA = z.object({
  message: z.string(),
});

const plugin: FastifyPluginAsyncZod = async (fastify, _opts) => {
  fastify.route({
    method: 'GET',
    url: '/message',
    // Define your schema
    schema: {
      querystring: MESSAGE_SCHEMA,
      response: {
        200: z.string(),
      },
    },
    handler: async (req, res) => {
      const response = await main(req.query.message);
      res.send(response);
    },
  });
};
export default plugin;
