namespace PdfToolkit.Services;

public static class PageRangeParser
{
    public static List<int> Parse(string text, int total)
    {
        var result = new HashSet<int>();
        foreach (var part in text.Split(','))
        {
            var trimmed = part.Trim();
            if (string.IsNullOrEmpty(trimmed)) continue;

            if (trimmed.Contains('-'))
            {
                var range = trimmed.Split('-');
                if (range.Length == 2 && int.TryParse(range[0], out var from) && int.TryParse(range[1], out var to)
                    && from >= 1 && to <= total)
                {
                    for (var i = from; i <= to; i++)
                        result.Add(i - 1);
                }
            }
            else if (int.TryParse(trimmed, out var page))
            {
                if (page >= 1 && page <= total)
                    result.Add(page - 1);
            }
        }
        return result.OrderBy(x => x).ToList();
    }
}
