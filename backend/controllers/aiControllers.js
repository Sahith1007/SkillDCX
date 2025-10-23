export const simpleAIResponse = (req, res) => {
  const { message } = req.body;
  return res.json({
    reply: `AI Bot received: "${message}"`
  });
};
