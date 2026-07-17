using PdfSharp.Pdf;
using PdfSharp.Pdf.IO;

namespace PdfToolkit.Models;

public class DocumentModel : IDisposable
{
    private PdfDocument? _document;
    private string? _filePath;

    public PdfDocument? Document => _document;
    public string? FilePath => _filePath;
    public int PageCount => _document?.PageCount ?? 0;
    public bool IsOpen => _document != null;

    public void Open(string path)
    {
        Close();
        _filePath = path;
        _document = PdfReader.Open(path, PdfDocumentOpenMode.Import);
    }

    public void Open(string path, string password)
    {
        Close();
        _filePath = path;
        _document = PdfReader.Open(path, password, PdfDocumentOpenMode.Import);
    }

    public void Close()
    {
        _document?.Dispose();
        _document = null;
        _filePath = null;
    }

    public void Dispose()
    {
        Close();
    }
}
