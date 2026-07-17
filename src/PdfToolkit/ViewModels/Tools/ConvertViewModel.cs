using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Docnet.Core;
using Docnet.Core.Models;
using PdfSharp.Drawing;
using PdfSharp.Pdf;
using PdfSharp.Pdf.IO;
using PdfToolkit.Services;

namespace PdfToolkit.ViewModels.Tools;

public partial class ConvertViewModel : ViewModelBase
{
    private readonly MainWindowViewModel _mainVm;

    [ObservableProperty]
    private string _conversionDirection = "PdfToImages";

    [ObservableProperty]
    private string _pageRange = string.Empty;

    [ObservableProperty]
    private string _outputFormat = "Png";

    [ObservableProperty]
    private int _dpi = 150;

    [ObservableProperty]
    private string _statusMessage = string.Empty;

    public ObservableCollection<string> ImagePaths { get; } = new();

    public ConvertViewModel(MainWindowViewModel mainVm)
    {
        _mainVm = mainVm;
    }

    public List<string> ConversionDirections { get; } = ["PdfToImages", "ImagesToPdf"];
    public List<string> OutputFormats { get; } = ["Png", "Jpeg", "Tiff"];

    [RelayCommand]
    private async Task ConvertAsync()
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

            var ext = OutputFormat.ToLowerInvariant() switch
            {
                "jpeg" => "jpg",
                "tiff" => "tiff",
                _ => "png"
            };
            var folder = Path.GetDirectoryName(sourcePath);
            var baseName = Path.GetFileNameWithoutExtension(sourcePath);

            using var docReader = DocLib.Instance.GetDocReader(sourcePath, new PageDimensions(Dpi / 72.0));

            var savedFiles = new List<string>();
            foreach (var pageNum in pages)
            {
                var pageReader = docReader.GetPageReader(pageNum - 1);
                var imageBytes = pageReader.GetImage();
                var outputPath = Path.Combine(folder!, $"{baseName}_page{pageNum}.{ext}");
                await File.WriteAllBytesAsync(outputPath, imageBytes);
                savedFiles.Add(outputPath);
            }

            StatusMessage = $"Saved {savedFiles.Count} image(s)";
            _mainVm.StatusText = $"Converted {savedFiles.Count} page(s) to images";
        }
        catch (Exception ex)
        {
            _mainVm.StatusText = $"Convert failed: {ex.Message}";
        }
    }

    [RelayCommand]
    private async Task CreatePdfAsync()
    {
        if (ImagePaths.Count == 0)
        {
            _mainVm.StatusText = "No images selected";
            return;
        }

        var savePath = await _mainVm.FileDialogService.SavePdfAsync(GetWindow(), "output.pdf");
        if (savePath == null) return;

        try
        {
            using var doc = new PdfDocument();

            foreach (var imagePath in ImagePaths)
            {
                using var image = XImage.FromFile(imagePath);
                var page = doc.AddPage();
                page.Width = XUnit.FromPoint(image.PointWidth);
                page.Height = XUnit.FromPoint(image.PointHeight);
                using var gfx = XGraphics.FromPdfPage(page);
                gfx.DrawImage(image, 0, 0);
            }

            doc.Save(savePath);
            StatusMessage = $"Created PDF with {ImagePaths.Count} page(s)";
            _mainVm.StatusText = $"Created {Path.GetFileName(savePath)} from {ImagePaths.Count} images";
        }
        catch (Exception ex)
        {
            _mainVm.StatusText = $"Create PDF failed: {ex.Message}";
        }
    }

    [RelayCommand]
    private async Task SelectImagesAsync()
    {
        var paths = await _mainVm.FileDialogService.OpenMultiImageAsync(GetWindow());
        foreach (var path in paths)
            ImagePaths.Add(path);

        StatusMessage = $"{ImagePaths.Count} image(s) selected";
    }
}
