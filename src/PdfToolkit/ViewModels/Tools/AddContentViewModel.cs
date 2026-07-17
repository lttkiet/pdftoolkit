using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using PdfSharp.Drawing;
using PdfSharp.Pdf;
using PdfSharp.Pdf.IO;
using PdfToolkit.Services;

namespace PdfToolkit.ViewModels.Tools;

public partial class AddContentViewModel : ViewModelBase
{
    private readonly MainWindowViewModel _mainVm;

    [ObservableProperty]
    private string _contentType = "Text";

    [ObservableProperty]
    private string _textContent = string.Empty;

    [ObservableProperty]
    private string _imagePath = string.Empty;

    [ObservableProperty]
    private double _xPosition = 72;

    [ObservableProperty]
    private double _yPosition = 72;

    [ObservableProperty]
    private double _fontSize = 12;

    [ObservableProperty]
    private double _imageWidth = 200;

    [ObservableProperty]
    private double _imageHeight = 200;

    [ObservableProperty]
    private string _pageRange = string.Empty;

    public AddContentViewModel(MainWindowViewModel mainVm)
    {
        _mainVm = mainVm;
    }

    public List<string> ContentTypes { get; } = ["Text", "Image"];

    private List<int> GetTargetPages(int totalPages)
    {
        if (string.IsNullOrWhiteSpace(PageRange))
        {
            return Enumerable.Range(0, totalPages).ToList();
        }
        return PageRangeParser.Parse(PageRange, totalPages);
    }

    [RelayCommand]
    private async Task AddTextAsync()
    {
        if (_mainVm.DocumentModel.Document == null || !_mainVm.DocumentModel.IsOpen)
        {
            _mainVm.StatusText = "No PDF open. Open a PDF first.";
            return;
        }

        if (string.IsNullOrWhiteSpace(TextContent))
        {
            _mainVm.StatusText = "Enter text to add.";
            return;
        }

        var savePath = await _mainVm.FileDialogService.SavePdfAsync(GetWindow(), "add_text.pdf");
        if (savePath == null) return;

        try
        {
            using var srcDoc = PdfReader.Open(_mainVm.DocumentModel.FilePath!, PdfDocumentOpenMode.Import);
            using var result = new PdfDocument();

            var indices = GetTargetPages(srcDoc.PageCount);
            foreach (var i in indices)
            {
                var page = result.AddPage(srcDoc.Pages[i]);
                using var gfx = XGraphics.FromPdfPage(page);
                var font = new XFont("Arial", FontSize);
                gfx.DrawString(TextContent, font, XBrushes.Black, new XPoint(XPosition, YPosition));
            }

            result.Save(savePath);
            _mainVm.StatusText = $"Added text to {indices.Count} page(s)";
        }
        catch (Exception ex)
        {
            _mainVm.StatusText = $"Add text failed: {ex.Message}";
        }
    }

    [RelayCommand]
    private async Task AddImageAsync()
    {
        if (_mainVm.DocumentModel.Document == null || !_mainVm.DocumentModel.IsOpen)
        {
            _mainVm.StatusText = "No PDF open. Open a PDF first.";
            return;
        }

        if (string.IsNullOrWhiteSpace(ImagePath) || !File.Exists(ImagePath))
        {
            _mainVm.StatusText = "Select a valid image file.";
            return;
        }

        var savePath = await _mainVm.FileDialogService.SavePdfAsync(GetWindow(), "add_image.pdf");
        if (savePath == null) return;

        try
        {
            using var srcDoc = PdfReader.Open(_mainVm.DocumentModel.FilePath!, PdfDocumentOpenMode.Import);
            using var result = new PdfDocument();

            var indices = GetTargetPages(srcDoc.PageCount);
            foreach (var i in indices)
            {
                var page = result.AddPage(srcDoc.Pages[i]);
                using var gfx = XGraphics.FromPdfPage(page);
                var image = XImage.FromFile(ImagePath);
                gfx.DrawImage(image, XPosition, YPosition, ImageWidth, ImageHeight);
            }

            result.Save(savePath);
            _mainVm.StatusText = $"Added image to {indices.Count} page(s)";
        }
        catch (Exception ex)
        {
            _mainVm.StatusText = $"Add image failed: {ex.Message}";
        }
    }

    [RelayCommand]
    private async Task SelectImageAsync()
    {
        var path = await _mainVm.FileDialogService.OpenImageAsync(GetWindow());
        if (path != null)
        {
            ImagePath = path;
        }
    }
}
