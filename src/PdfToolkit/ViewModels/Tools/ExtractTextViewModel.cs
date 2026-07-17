using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Docnet.Core;
using Docnet.Core.Models;
using PdfSharp.Pdf.IO;
using PdfToolkit.Services;

namespace PdfToolkit.ViewModels.Tools;

public partial class ExtractTextViewModel : ViewModelBase
{
    private readonly MainWindowViewModel _mainVm;

    [ObservableProperty]
    private string _pageRange = string.Empty;

    [ObservableProperty]
    private string _extractedText = string.Empty;

    public ExtractTextViewModel(MainWindowViewModel mainVm)
    {
        _mainVm = mainVm;
    }

    [RelayCommand]
    private async Task ExtractAsync()
    {
        string? sourcePath = null;

        if (_mainVm.DocumentModel.IsOpen)
        {
            sourcePath = _mainVm.DocumentModel.FilePath;
        }
        else
        {
            sourcePath = await _mainVm.FileDialogService.OpenPdfAsync(GetWindow());
        }

        if (sourcePath == null)
        {
            _mainVm.StatusText = "No PDF file selected";
            return;
        }

        try
        {
            int pageCount;
            using (var pdfDoc = PdfReader.Open(sourcePath, PdfDocumentOpenMode.Import))
            {
                pageCount = pdfDoc.PageCount;
            }

            var pages = string.IsNullOrWhiteSpace(PageRange)
                ? Enumerable.Range(1, pageCount).ToList()
                : PageRangeParser.Parse(PageRange, pageCount).Select(i => i + 1).ToList();

            if (pages.Count == 0)
            {
                _mainVm.StatusText = "No valid pages in range";
                return;
            }

            using var docReader = DocLib.Instance.GetDocReader(sourcePath, new PageDimensions(1.0));

            var sb = new System.Text.StringBuilder();
            foreach (var pageNum in pages)
            {
                var pageReader = docReader.GetPageReader(pageNum - 1);
                var text = pageReader.GetText();
                sb.AppendLine($"--- Page {pageNum} ---");
                sb.AppendLine(text);
                sb.AppendLine();
            }

            ExtractedText = sb.ToString().TrimEnd();
            _mainVm.StatusText = $"Extracted text from {pages.Count} page(s)";
        }
        catch (Exception ex)
        {
            _mainVm.StatusText = $"Extract failed: {ex.Message}";
        }
    }

    [RelayCommand]
    private async Task SaveAsync()
    {
        if (string.IsNullOrWhiteSpace(ExtractedText))
        {
            _mainVm.StatusText = "No text to save";
            return;
        }

        var savePath = await _mainVm.FileDialogService.SaveTextAsync(GetWindow(), "extracted.txt");
        if (savePath == null) return;

        try
        {
            await File.WriteAllTextAsync(savePath, ExtractedText);
            _mainVm.StatusText = $"Saved to {Path.GetFileName(savePath)}";
        }
        catch (Exception ex)
        {
            _mainVm.StatusText = $"Save failed: {ex.Message}";
        }
    }
}
