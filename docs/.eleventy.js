const fs = require('fs');
const path = require('path');

module.exports = function(eleventyConfig) {
  // Passthrough: site-level static assets
  eleventyConfig.addPassthroughCopy({ 'site/assets': 'docs/assets' });
  eleventyConfig.addPassthroughCopy({ 'site/images': 'docs/images' });
  eleventyConfig.addPassthroughCopy({ 'site/fonts': 'docs/fonts' });
  eleventyConfig.addPassthroughCopy({ 'site/app.js': 'docs/app.js' });
  eleventyConfig.addPassthroughCopy({ 'site/CsvToTable.js': 'docs/CsvToTable.js' });
  eleventyConfig.addPassthroughCopy({ 'site/styles.css': 'docs/styles.css' });
  eleventyConfig.addPassthroughCopy({ 'site/dictionary.csv': 'docs/dictionary.csv' });
  eleventyConfig.addPassthroughCopy({ 'site/ipa_map.csv': 'docs/ipa_map.csv' });
  // Only copy specific guide assets; templates in site/guide are rendered
  eleventyConfig.addPassthroughCopy({ 'site/guide/guide.js': 'docs/guide/guide.js' });
  eleventyConfig.addPassthroughCopy({ 'site/guide/guide.pdf': 'docs/guide/guide.pdf' });
  eleventyConfig.addPassthroughCopy({ 'site/guide.pdf': 'docs/guide.pdf' });

  // No custom shortcodes required currently.



  return {
    dir: {
      input: 'site',
      output: 'docs',
      includes: '_includes'
    },
    templateFormats: [
      'njk', 'md', 'html'
    ]
  };
};
