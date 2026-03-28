module.exports = function(eleventyConfig) {
  // Pass through static assets
  eleventyConfig.addPassthroughCopy("*.css");
  eleventyConfig.addPassthroughCopy("*.svg");
  eleventyConfig.addPassthroughCopy("*.ico");
  eleventyConfig.addPassthroughCopy("robots.txt");
  // sitemap.xml is now generated dynamically via sitemap.njk — not a passthrough
  eleventyConfig.addPassthroughCopy("apple-redesign.css");

  // Pass through tool directories (plain HTML tools)
  eleventyConfig.addPassthroughCopy("json-formatter");
  eleventyConfig.addPassthroughCopy("jwt-debugger");
  eleventyConfig.addPassthroughCopy("base64-converter");
  eleventyConfig.addPassthroughCopy("timestamp-converter");
  eleventyConfig.addPassthroughCopy("password-generator");
  eleventyConfig.addPassthroughCopy("url-encoder");
  eleventyConfig.addPassthroughCopy("color-converter");
  eleventyConfig.addPassthroughCopy("cron-generator");
  eleventyConfig.addPassthroughCopy("html-entities");
  eleventyConfig.addPassthroughCopy("regex-tester");
  eleventyConfig.addPassthroughCopy("pdf-tools");
  eleventyConfig.addPassthroughCopy("ai-sanitizer");

  // Blog collection sorted by date descending
  eleventyConfig.addCollection("blog", function(collectionApi) {
    return collectionApi.getFilteredByGlob("blog/*.md").reverse();
  });

  // Date filter for templates
  eleventyConfig.addFilter("dateFormat", function(date) {
    return new Date(date).toLocaleDateString("en-US", {
      year: "numeric", month: "long", day: "numeric"
    });
  });

  // ISO date filter for sitemap (YYYY-MM-DD)
  eleventyConfig.addFilter("isoDate", function(date) {
    return new Date(date).toISOString().split("T")[0];
  });

  // RFC 2822 date filter for RSS feed
  eleventyConfig.addFilter("rfc2822", function(date) {
    return new Date(date).toUTCString();
  });

  return {
    dir: {
      input: ".",
      output: "_site",
      includes: "_includes",
      layouts: "_layouts"
    },
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk"
  };
};
