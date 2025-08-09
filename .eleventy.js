const fs = require('fs');
const path = require('path');

module.exports = function(eleventyConfig) {
  // Passthrough: site-level static assets
  eleventyConfig.addPassthroughCopy({ 'site/assets': 'assets' });
  eleventyConfig.addPassthroughCopy({ 'site/images': 'images' });
  eleventyConfig.addPassthroughCopy({ 'site/fonts': 'fonts' });
  eleventyConfig.addPassthroughCopy({ 'site/app.js': 'app.js' });
  eleventyConfig.addPassthroughCopy({ 'site/CsvToTable.js': 'CsvToTable.js' });
  eleventyConfig.addPassthroughCopy({ 'site/styles.css': 'styles.css' });
  eleventyConfig.addPassthroughCopy({ 'site/dictionary.csv': 'dictionary.csv' });
  eleventyConfig.addPassthroughCopy({ 'site/ipa_map.csv': 'ipa_map.csv' });
  // Only copy specific guide assets; templates in site/guide are rendered
  eleventyConfig.addPassthroughCopy({ 'site/guide/guide.js': 'guide/guide.js' });
  eleventyConfig.addPassthroughCopy({ 'site/guide/guide.pdf': 'guide/guide.pdf' });
  eleventyConfig.addPassthroughCopy({ 'site/guide.pdf': 'guide.pdf' });

  // No custom shortcodes required currently.



  return {
    dir: {
      input: 'site',
      output: 'docs',
      includes: '_includes'
    },
    templateFormats: [
      'njk', 'md', 'html'
    ],
    pathPrefix: "/tovian"
  };
};
