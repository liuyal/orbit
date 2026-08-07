import { LanguageSupport, StreamLanguage, StreamParser } from '@codemirror/language';

/**
 * Custom Gherkin tokenizer.
 *
 * The upstream `@codemirror/legacy-modes` Gherkin mode only recognizes
 * `Given`/`When`/`Then`/`And`/`But` steps once it has already seen a
 * `Feature:`/`Background:`/`Scenario:` header on a previous line. Test
 * scripts stored on a single test case are usually just a bare list of
 * steps with no surrounding feature/scenario wrapper, so that mode ends up
 * leaving almost the entire script unstyled. This tokenizer highlights
 * keywords, tags, strings, placeholders, comments and tables independent
 * of any preceding section header.
 */
interface GherkinState {
  inMultilineString: boolean;
  inTable: boolean;
  lineStart: boolean;
}

const SECTION_KEYWORDS = /^(Feature|Rule|Background|Scenario Outline|Scenario|Examples):?/;
const STEP_KEYWORDS = /^(Given|When|Then|And|But)\b|^\*(?=\s|$)/;

export const gherkinStreamParser: StreamParser<GherkinState> = {
  name: 'gherkin',

  startState(): GherkinState {
    return { inMultilineString: false, inTable: false, lineStart: true };
  },

  token(stream, state): string | null {
    if (stream.sol()) {
      state.lineStart = true;
      state.inTable = /^\s*\|/.test(stream.string);
    }

    if (stream.eatSpace()) return null;

    if (state.inMultilineString) {
      state.lineStart = false;
      if (stream.match('"""')) {
        state.inMultilineString = false;
      } else {
        stream.skipToEnd();
      }
      return 'string';
    }

    if (stream.match('"""')) {
      state.inMultilineString = true;
      state.lineStart = false;
      return 'string';
    }

    if (state.inTable) {
      state.lineStart = false;
      if (stream.match(/^\|/)) return 'bracket';
      stream.match(/^[^|]+/);
      return 'string';
    }

    if (stream.match(/^#.*/)) {
      state.lineStart = false;
      return 'comment';
    }

    if (stream.match(/^@\S+/)) {
      state.lineStart = false;
      return 'tag';
    }

    if (state.lineStart) {
      state.lineStart = false;
      if (stream.match(SECTION_KEYWORDS)) return 'keyword';
      if (stream.match(STEP_KEYWORDS)) return 'keyword';
    }

    if (stream.match(/^"[^"]*"?/)) return 'string';
    if (stream.match(/^<[^>]*>?/)) return 'variable';

    stream.next();
    stream.eatWhile(/[^@"<#|]/);
    return null;
  },

  languageData: {
    commentTokens: { line: '#' },
  },
};

export function gherkinLanguage(): LanguageSupport {
  return new LanguageSupport(StreamLanguage.define(gherkinStreamParser));
}
