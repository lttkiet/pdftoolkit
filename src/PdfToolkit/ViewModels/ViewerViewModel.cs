using Avalonia.Media.Imaging;
using Docnet.Core;
using Docnet.Core.Readers;

namespace PdfToolkit.ViewModels;

public partial class ViewerViewModel : ViewModelBase
{
    private readonly MainWindowViewModel _mainVm;
    private IDocReader? _docReader;
    private int _currentPageIndex;
    private int _totalPages;
    private double _zoomLevel = 1.5;
    private Bitmap? _currentPageImage;

    public ViewerViewModel(MainWindowViewModel mainVm)
    {
        _mainVm = mainVm;
    }

    public int CurrentPageIndex
    {
        get => _currentPageIndex;
        set
        {
            if (SetProperty(ref _currentPageIndex, value))
            {
                OnPropertyChanged(nameof(PageIndicator));
                RenderCurrentPage();
            }
        }
    }

    public int TotalPages
    {
        get => _totalPages;
        set => SetProperty(ref _totalPages, value);
    }

    public double ZoomLevel
    {
        get => _zoomLevel;
        set
        {
            if (SetProperty(ref _zoomLevel, Math.Clamp(value, 0.3, 5.0)))
                RenderCurrentPage();
        }
    }

    public string PageIndicator => TotalPages > 0
        ? $"{_currentPageIndex + 1} / {_totalPages}"
        : "No document loaded";

    public Bitmap? CurrentPageImage
    {
        get => _currentPageImage;
        set => SetProperty(ref _currentPageImage, value);
    }

    private List<Bitmap> _thumbnails = [];
    public List<Bitmap> Thumbnails
    {
        get => _thumbnails;
        set => SetProperty(ref _thumbnails, value);
    }

    public void LoadDocument()
    {
        var path = _mainVm.DocumentModel.FilePath;
        if (path == null) return;

        _docReader?.Dispose();
        _docReader = DocLib.Instance.GetDocReader(path, new Docnet.Core.Models.PageDimensions(1.0));

        TotalPages = _docReader.GetPageCount();
        _currentPageIndex = 0;
        OnPropertyChanged(nameof(PageIndicator));
        GenerateThumbnails();
        RenderCurrentPage();
    }

    public void GoToPage(int index)
    {
        if (index >= 0 && index < TotalPages)
            CurrentPageIndex = index;
    }

    public void PreviousPage() => GoToPage(CurrentPageIndex - 1);
    public void NextPage() => GoToPage(CurrentPageIndex + 1);
    public void ZoomIn() => ZoomLevel *= 1.2;
    public void ZoomOut() => ZoomLevel /= 1.2;

    private void GenerateThumbnails()
    {
        Thumbnails.ForEach(t => t.Dispose());
        Thumbnails.Clear();

        if (_docReader == null) return;

        for (var i = 0; i < TotalPages; i++)
        {
            var thumb = RenderPage(i, 0.25);
            if (thumb != null)
                Thumbnails.Add(thumb);
        }
        OnPropertyChanged(nameof(Thumbnails));
    }

    private void RenderCurrentPage()
    {
        if (_docReader == null || _currentPageIndex >= TotalPages) return;

        var newImage = RenderPage(_currentPageIndex, _zoomLevel);
        var old = _currentPageImage;
        CurrentPageImage = newImage;
        old?.Dispose();
    }

    private Bitmap? RenderPage(int pageIndex, double scale)
    {
        if (_docReader == null) return null;

        var pageReader = _docReader.GetPageReader(pageIndex);
        var width = (int)(pageReader.GetPageWidth() * scale);
        var height = (int)(pageReader.GetPageHeight() * scale);

        var imageBytes = pageReader.GetImage();

        using var ms = new MemoryStream(imageBytes);
        return new Bitmap(ms);
    }

    public void Dispose()
    {
        Thumbnails.ForEach(t => t.Dispose());
        _currentPageImage?.Dispose();
        _docReader?.Dispose();
    }
}
